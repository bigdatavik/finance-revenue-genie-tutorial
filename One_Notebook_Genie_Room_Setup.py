# Databricks notebook source
# MAGIC %md
# MAGIC # Genie Room Tutorial – One Notebook Setup (Finance & Revenue)
# MAGIC
# MAGIC **Tutorial / shareable setup** — creates the **Genie Room Tutorial - Finance & Revenue** room: schema (if needed), tables, synthetic data, `config_genie`, and the Genie space.
# MAGIC
# MAGIC - **Catalog:** Default `humana_payer` (already created). Provide your own catalog if different.
# MAGIC - **Schema:** Created if it does not exist, or reused if it does.
# MAGIC - **Not part of the main pipeline** — run manually or share for tutorials.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuration (edit these and run)

# COMMAND ----------

# ----- Edit these to match your workspace -----
# Catalog: already created; use humana_payer or your own.
CATALOG = "humana_payer"
# Schema: created if not exists, or reused.
SCHEMA = "finance_revenue_tutorial"
WAREHOUSE_ID = "your-warehouse-id"  # SQL Warehouse ID from Databricks
GENIE_DISPLAY_NAME = "Genie Room Tutorial - Finance & Revenue"
GENIE_DESCRIPTION = "Query payer finance and revenue metrics with natural language (tutorial)"

# Optional: seed row counts (defaults shown)
NUM_PRODUCTS = 12
NUM_MONTHS = 24  # 2 years of monthly data
NUM_REGIONS = 4

# COMMAND ----------

# Derived table names (do not edit)
BASE = f"{CATALOG}.{SCHEMA}"
MEMBERSHIP_FACT_TABLE = f"{BASE}.membership_fact"
REVENUE_FACT_TABLE = f"{BASE}.revenue_fact"
MLR_FACT_TABLE = f"{BASE}.mlr_fact"
RESERVES_FACT_TABLE = f"{BASE}.reserves_fact"
PRODUCT_DIM_TABLE = f"{BASE}.product_dim"
CONFIG_TABLE = f"{BASE}.config_genie"

print(f"Catalog: {CATALOG}, Schema: {SCHEMA}")
print(f"Warehouse: {WAREHOUSE_ID}")
print(f"Genie: {GENIE_DISPLAY_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Use catalog; create schema if not exists, then use schema

# COMMAND ----------

spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"USE SCHEMA {SCHEMA}")
print(f"Using {CATALOG}.{SCHEMA} (schema created or reused)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create tables (five for Genie + config_genie)

# COMMAND ----------

# Dimension: product_dim
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {PRODUCT_DIM_TABLE} (
  product_id STRING,
  product_name STRING,
  product_type STRING,
  lob STRING,
  active_flag BOOLEAN
) USING DELTA
COMMENT 'Product dimension for Finance & Revenue Genie room'
""")
print(f"Table {PRODUCT_DIM_TABLE} OK")

# COMMAND ----------

# Fact: membership_fact
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {MEMBERSHIP_FACT_TABLE} (
  member_month_id STRING,
  product_id STRING,
  lob STRING,
  region STRING,
  period_month DATE,
  member_months INT,
  enrollment_count INT,
  segment STRING
) USING DELTA
COMMENT 'Membership fact table with member months and enrollment counts'
""")
print(f"Table {MEMBERSHIP_FACT_TABLE} OK")

# COMMAND ----------

# Fact: revenue_fact
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {REVENUE_FACT_TABLE} (
  revenue_id STRING,
  product_id STRING,
  lob STRING,
  period_month DATE,
  premium_revenue DOUBLE,
  other_revenue DOUBLE,
  total_revenue DOUBLE
) USING DELTA
COMMENT 'Revenue fact table with premium and other revenue'
""")
print(f"Table {REVENUE_FACT_TABLE} OK")

# COMMAND ----------

# Fact: mlr_fact
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {MLR_FACT_TABLE} (
  mlr_id STRING,
  product_id STRING,
  lob STRING,
  region STRING,
  period_month DATE,
  medical_cost DOUBLE,
  premium_revenue DOUBLE,
  mlr_pct DOUBLE
) USING DELTA
COMMENT 'Medical Loss Ratio fact table'
""")
print(f"Table {MLR_FACT_TABLE} OK")

# COMMAND ----------

# Fact: reserves_fact
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {RESERVES_FACT_TABLE} (
  reserve_id STRING,
  reserve_type STRING,
  product_id STRING,
  period_month DATE,
  beginning_balance DOUBLE,
  ending_balance DOUBLE,
  reserve_movement DOUBLE
) USING DELTA
COMMENT 'Reserves fact table with balances and movements'
""")
print(f"Table {RESERVES_FACT_TABLE} OK")

# COMMAND ----------

# config_genie: key/value for Genie space ID (written after creating the space)
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CONFIG_TABLE} (
  config_key STRING NOT NULL,
  config_value STRING NOT NULL,
  created_at TIMESTAMP NOT NULL,
  CONSTRAINT config_genie_pk PRIMARY KEY(config_key)
)
USING DELTA
COMMENT 'Configuration for Genie room (e.g. genie_space_id)'
""")
print(f"Table {CONFIG_TABLE} OK")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3b. Create metric view (mv_financial_performance)

# COMMAND ----------

# Create a base view that joins the key fact tables for the metric view
BASE_VIEW = f"{BASE}.v_financial_base"
spark.sql(f"""
CREATE OR REPLACE VIEW {BASE_VIEW} AS
SELECT
  p.product_type,
  r.lob,
  m.region,
  r.period_month,
  r.premium_revenue,
  r.total_revenue,
  mlr.medical_cost,
  mlr.mlr_pct,
  m.member_months
FROM {REVENUE_FACT_TABLE} r
JOIN {PRODUCT_DIM_TABLE} p ON r.product_id = p.product_id
LEFT JOIN {MLR_FACT_TABLE} mlr ON r.product_id = mlr.product_id AND r.lob = mlr.lob AND r.period_month = mlr.period_month
LEFT JOIN {MEMBERSHIP_FACT_TABLE} m ON r.product_id = m.product_id AND r.lob = m.lob AND r.period_month = m.period_month
""")
print(f"Base view {BASE_VIEW} OK")

# COMMAND ----------

# Metric view: mv_financial_performance
MV_FINANCIAL_PERFORMANCE = f"{BASE}.mv_financial_performance"
yaml_spec = f"""
version: 1.1
comment: "Financial performance metrics: revenue, MLR, membership, PMPM (tutorial)"
source: {BASE_VIEW}
dimensions:
  - name: product_type
    expr: product_type
  - name: lob
    expr: lob
  - name: region
    expr: region
  - name: period_month
    expr: period_month
measures:
  - name: total_premium
    expr: sum(premium_revenue)
  - name: total_revenue
    expr: sum(total_revenue)
  - name: total_medical_cost
    expr: sum(medical_cost)
  - name: mlr_pct_avg
    expr: avg(mlr_pct)
  - name: member_months_total
    expr: sum(member_months)
  - name: pmpm_revenue
    expr: MEASURE(total_revenue) / nullif(MEASURE(member_months_total), 0)
"""

spark.sql(f"""
CREATE OR REPLACE VIEW {MV_FINANCIAL_PERFORMANCE}
WITH METRICS
LANGUAGE YAML
AS $$
{yaml_spec}
$$
""")
print(f"Metric view {MV_FINANCIAL_PERFORMANCE} OK")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Seed synthetic data

# COMMAND ----------

import random
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, DateType

random.seed(42)

# Reference data
regions = ["South", "Midwest", "Northeast", "West"]
lobs = ["MA", "PDP", "MAPD", "Commercial", "Medicaid"]
segments = ["Individual", "Group", "Dual Eligible", "Low Income Subsidy"]
reserve_types = ["IBNR", "Premium Deficiency", "Claim Liability"]

# Generate period months (last 24 months)
today = date.today().replace(day=1)
period_months = [(today - relativedelta(months=i)) for i in range(NUM_MONTHS)]
period_months.reverse()  # oldest first

# COMMAND ----------

# Product dimension
products = [
    ("prod_001", "MA Basic", "MA", "MA", True),
    ("prod_002", "MA Plus", "MA", "MA", True),
    ("prod_003", "MA Premium", "MA", "MA", True),
    ("prod_004", "PDP Standard", "PDP", "PDP", True),
    ("prod_005", "PDP Enhanced", "PDP", "PDP", True),
    ("prod_006", "MAPD Value", "MAPD", "MAPD", True),
    ("prod_007", "MAPD Preferred", "MAPD", "MAPD", True),
    ("prod_008", "MAPD Elite", "MAPD", "MAPD", False),  # inactive
    ("prod_009", "Commercial HMO", "Commercial", "Commercial", True),
    ("prod_010", "Commercial PPO", "Commercial", "Commercial", True),
    ("prod_011", "Medicaid Standard", "Medicaid", "Medicaid", True),
    ("prod_012", "Medicaid Plus", "Medicaid", "Medicaid", True),
]

product_schema = StructType([
    StructField("product_id", StringType()),
    StructField("product_name", StringType()),
    StructField("product_type", StringType()),
    StructField("lob", StringType()),
    StructField("active_flag", BooleanType()),
])
spark.createDataFrame(products, product_schema).write.mode("overwrite").saveAsTable(PRODUCT_DIM_TABLE)
print(f"Wrote {len(products)} rows to {PRODUCT_DIM_TABLE}")

# COMMAND ----------

# Membership fact - member months and enrollment by product/lob/region/month
membership_rows = []
member_month_id = 0

for product_id, product_name, product_type, lob, active in products:
    if not active:
        continue
    for region in regions:
        for period in period_months:
            member_month_id += 1
            # Base member months varies by product type
            base_members = {
                "MA": random.randint(8000, 15000),
                "PDP": random.randint(3000, 8000),
                "MAPD": random.randint(10000, 20000),
                "Commercial": random.randint(5000, 12000),
                "Medicaid": random.randint(6000, 10000),
            }.get(product_type, 5000)

            # Add some growth trend and seasonality
            month_factor = 1 + (period_months.index(period) * 0.005)  # slight growth
            seasonal_factor = 1 + (0.1 if period.month in [1, 10, 11, 12] else 0)  # AEP bump
            member_months = int(base_members * month_factor * seasonal_factor * random.uniform(0.9, 1.1))
            enrollment_count = int(member_months * random.uniform(0.95, 1.05))
            segment = random.choice(segments)

            membership_rows.append((
                f"mm_{member_month_id:06d}",
                product_id,
                lob,
                region,
                period,
                member_months,
                enrollment_count,
                segment,
            ))

membership_schema = StructType([
    StructField("member_month_id", StringType()),
    StructField("product_id", StringType()),
    StructField("lob", StringType()),
    StructField("region", StringType()),
    StructField("period_month", DateType()),
    StructField("member_months", IntegerType()),
    StructField("enrollment_count", IntegerType()),
    StructField("segment", StringType()),
])
spark.createDataFrame(membership_rows, membership_schema).write.mode("overwrite").saveAsTable(MEMBERSHIP_FACT_TABLE)
print(f"Wrote {len(membership_rows)} rows to {MEMBERSHIP_FACT_TABLE}")

# COMMAND ----------

# Revenue fact - premium and other revenue by product/lob/month
revenue_rows = []
revenue_id = 0

# PMPM rates by product type (monthly premium per member)
pmpm_rates = {
    "MA": (800, 1200),
    "PDP": (30, 60),
    "MAPD": (900, 1400),
    "Commercial": (400, 700),
    "Medicaid": (200, 400),
}

for product_id, product_name, product_type, lob, active in products:
    if not active:
        continue
    for period in period_months:
        revenue_id += 1
        pmpm_low, pmpm_high = pmpm_rates.get(product_type, (300, 600))
        pmpm = random.uniform(pmpm_low, pmpm_high)

        # Get member months for this product/lob/period (approximate)
        base_members = {
            "MA": 12000, "PDP": 5500, "MAPD": 15000, "Commercial": 8500, "Medicaid": 8000
        }.get(product_type, 8000) * len(regions)

        premium_revenue = round(base_members * pmpm, 2)
        other_revenue = round(premium_revenue * random.uniform(0.02, 0.08), 2)  # 2-8% other revenue
        total_revenue = premium_revenue + other_revenue

        revenue_rows.append((
            f"rev_{revenue_id:06d}",
            product_id,
            lob,
            period,
            premium_revenue,
            other_revenue,
            total_revenue,
        ))

revenue_schema = StructType([
    StructField("revenue_id", StringType()),
    StructField("product_id", StringType()),
    StructField("lob", StringType()),
    StructField("period_month", DateType()),
    StructField("premium_revenue", DoubleType()),
    StructField("other_revenue", DoubleType()),
    StructField("total_revenue", DoubleType()),
])
spark.createDataFrame(revenue_rows, revenue_schema).write.mode("overwrite").saveAsTable(REVENUE_FACT_TABLE)
print(f"Wrote {len(revenue_rows)} rows to {REVENUE_FACT_TABLE}")

# COMMAND ----------

# MLR fact - medical cost and MLR by product/lob/region/month
mlr_rows = []
mlr_id = 0

# Target MLR by product type
target_mlr = {
    "MA": (0.82, 0.88),
    "PDP": (0.78, 0.85),
    "MAPD": (0.83, 0.89),
    "Commercial": (0.75, 0.82),
    "Medicaid": (0.88, 0.94),
}

for product_id, product_name, product_type, lob, active in products:
    if not active:
        continue
    for region in regions:
        for period in period_months:
            mlr_id += 1
            mlr_low, mlr_high = target_mlr.get(product_type, (0.80, 0.86))

            # Regional variation
            region_factor = {"South": 1.02, "Midwest": 0.98, "Northeast": 1.05, "West": 1.00}.get(region, 1.0)

            # Get approximate premium for this slice
            pmpm_low, pmpm_high = pmpm_rates.get(product_type, (300, 600))
            base_members = {
                "MA": 12000, "PDP": 5500, "MAPD": 15000, "Commercial": 8500, "Medicaid": 8000
            }.get(product_type, 8000)

            premium_revenue = round(base_members * random.uniform(pmpm_low, pmpm_high), 2)
            mlr_pct = random.uniform(mlr_low, mlr_high) * region_factor
            mlr_pct = min(mlr_pct, 0.98)  # cap at 98%
            medical_cost = round(premium_revenue * mlr_pct, 2)

            mlr_rows.append((
                f"mlr_{mlr_id:06d}",
                product_id,
                lob,
                region,
                period,
                medical_cost,
                premium_revenue,
                round(mlr_pct * 100, 2),  # as percentage
            ))

mlr_schema = StructType([
    StructField("mlr_id", StringType()),
    StructField("product_id", StringType()),
    StructField("lob", StringType()),
    StructField("region", StringType()),
    StructField("period_month", DateType()),
    StructField("medical_cost", DoubleType()),
    StructField("premium_revenue", DoubleType()),
    StructField("mlr_pct", DoubleType()),
])
spark.createDataFrame(mlr_rows, mlr_schema).write.mode("overwrite").saveAsTable(MLR_FACT_TABLE)
print(f"Wrote {len(mlr_rows)} rows to {MLR_FACT_TABLE}")

# COMMAND ----------

# Reserves fact - reserve balances and movements by type/product/month
reserves_rows = []
reserve_id = 0

for product_id, product_name, product_type, lob, active in products:
    if not active:
        continue
    for reserve_type in reserve_types:
        # Initial balance varies by reserve type and product
        base_balance = {
            "IBNR": random.uniform(5000000, 15000000),
            "Premium Deficiency": random.uniform(1000000, 5000000),
            "Claim Liability": random.uniform(3000000, 10000000),
        }.get(reserve_type, 5000000)

        current_balance = base_balance

        for period in period_months:
            reserve_id += 1
            beginning_balance = current_balance

            # Movement: slight increase with some volatility
            movement_pct = random.uniform(-0.03, 0.05)  # -3% to +5%
            reserve_movement = round(beginning_balance * movement_pct, 2)
            ending_balance = round(beginning_balance + reserve_movement, 2)

            reserves_rows.append((
                f"res_{reserve_id:06d}",
                reserve_type,
                product_id,
                period,
                round(beginning_balance, 2),
                ending_balance,
                reserve_movement,
            ))

            current_balance = ending_balance

reserves_schema = StructType([
    StructField("reserve_id", StringType()),
    StructField("reserve_type", StringType()),
    StructField("product_id", StringType()),
    StructField("period_month", DateType()),
    StructField("beginning_balance", DoubleType()),
    StructField("ending_balance", DoubleType()),
    StructField("reserve_movement", DoubleType()),
])
spark.createDataFrame(reserves_rows, reserves_schema).write.mode("overwrite").saveAsTable(RESERVES_FACT_TABLE)
print(f"Wrote {len(reserves_rows)} rows to {RESERVES_FACT_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create Genie space

# COMMAND ----------

# MAGIC %pip install databricks-sdk --quiet

# COMMAND ----------

import json
import uuid
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# COMMAND ----------

# Drop and recreate only the Genie room created by this notebook (title == GENIE_DISPLAY_NAME).
try:
    resp = w.api_client.do("GET", "/api/2.0/genie/spaces")
    for space in resp.get("spaces", []):
        if space.get("title") == GENIE_DISPLAY_NAME:
            old_id = space.get("space_id")
            w.api_client.do("DELETE", f"/api/2.0/genie/spaces/{old_id}")
            print(f"Deleted existing space '{GENIE_DISPLAY_NAME}' ({old_id})")
            break
except Exception as e:
    print(f"Check/delete existing: {e}")

# COMMAND ----------

# Build serialized_space (tables + metric view, sorted by identifier per API)
tables_sorted = sorted(
    [
        {"identifier": MEMBERSHIP_FACT_TABLE},
        {"identifier": REVENUE_FACT_TABLE},
        {"identifier": MLR_FACT_TABLE},
        {"identifier": RESERVES_FACT_TABLE},
        {"identifier": PRODUCT_DIM_TABLE},
        {"identifier": MV_FINANCIAL_PERFORMANCE},
    ],
    key=lambda x: x["identifier"],
)

text_instructions = f"""This space queries Payer Finance & Revenue data. Tables in {CATALOG}.{SCHEMA}:
1. membership_fact: member_month_id, product_id, lob, region, period_month, member_months, enrollment_count, segment
2. revenue_fact: revenue_id, product_id, lob, period_month, premium_revenue, other_revenue, total_revenue
3. mlr_fact: mlr_id, product_id, lob, region, period_month, medical_cost, premium_revenue, mlr_pct
4. reserves_fact: reserve_id, reserve_type, product_id, period_month, beginning_balance, ending_balance, reserve_movement
5. product_dim: product_id, product_name, product_type, lob, active_flag
6. mv_financial_performance (metric view): dimensions product_type, lob, region, period_month; measures total_premium, total_revenue, total_medical_cost, mlr_pct_avg, member_months_total, pmpm_revenue. Prefer for common KPIs and rollups.

Key concepts: MLR = medical cost / premium (lower is better); PMPM = per member per month; LOB = line of business (MA, PDP, MAPD, Commercial, Medicaid).

Use these for aggregations and filters. No carrier or client names in queries."""

serialized_space = {
    "version": 1,
    "config": {
        "sample_questions": [
            {"id": str(uuid.uuid4()).replace("-", ""), "question": ["Revenue by product and month"]},
            {"id": str(uuid.uuid4()).replace("-", ""), "question": ["MLR by line of business"]},
            {"id": str(uuid.uuid4()).replace("-", ""), "question": ["Membership trend by product"]},
            {"id": str(uuid.uuid4()).replace("-", ""), "question": ["Reserve movement by quarter"]},
            {"id": str(uuid.uuid4()).replace("-", ""), "question": ["Premium per member per month by LOB"]}
        ]
    },
    "instructions": {
        "text_instructions": [
            {"id": str(uuid.uuid4()).replace("-", ""), "content": [text_instructions]}
        ]
    },
    "data_sources": {
        "tables": tables_sorted
    }
}

payload = {
    "title": GENIE_DISPLAY_NAME,
    "description": GENIE_DESCRIPTION,
    "warehouse_id": WAREHOUSE_ID,
    "serialized_space": json.dumps(serialized_space)
}

response = w.api_client.do("POST", "/api/2.0/genie/spaces", body=payload)
GENIE_SPACE_ID = response.get("space_id")
print(f"Genie Space created: {GENIE_SPACE_ID}")

# COMMAND ----------

# Save genie_space_id to config_genie
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"USE SCHEMA {SCHEMA}")
spark.sql(f"""
MERGE INTO {CONFIG_TABLE} t
USING (
  SELECT 'genie_space_id' as config_key, '{GENIE_SPACE_ID}' as config_value, current_timestamp() as created_at
) s
ON t.config_key = s.config_key
WHEN MATCHED THEN UPDATE SET t.config_value = s.config_value, t.created_at = s.created_at
WHEN NOT MATCHED THEN INSERT (config_key, config_value, created_at) VALUES (s.config_key, s.config_value, s.created_at)
""")
print(f"Genie space ID saved to {CONFIG_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Done
# MAGIC
# MAGIC Next: use the docs in this folder to refine the Genie room (Instructions, Joins, UDFs) and follow **GENIE_ROOM_COMPLETE_GUIDE.md** to explore the room step by step.
# MAGIC
# MAGIC **Manual:** If an app uses this Genie room, grant **Can Run** on this Genie space to the app's service principal (Share → add principal → Can Run).
