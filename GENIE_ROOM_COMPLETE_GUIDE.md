# Genie Room Tutorial – Complete Guide (Finance & Revenue)

**Use this guide** so you can run the notebook, configure the **Genie Room Tutorial - Finance & Revenue**, and explore it end-to-end.

**Convention:** Replace `YOUR_CATALOG.YOUR_SCHEMA` everywhere with your catalog and schema (e.g. `humana_payer.finance_revenue_tutorial`).

**Printing:** This guide is formatted so content is not cut off when printed in portrait. Wide tables are split into blocks or lists; long SQL is in code blocks so it wraps.

---

## Quick start (4 steps)

1. **Edit** the notebook `One_Notebook_Genie_Room_Setup.py`: set `CATALOG`, `SCHEMA`, and `WAREHOUSE_ID`.
2. **Run** the notebook from top to bottom (creates schema, tables, data, metric view, Genie space).
3. **Configure** the room in Databricks Genie (Instructions → Text, Joins, SQL Expressions, SQL Queries, Benchmarks) using the sections below.
4. **Explore** the room: start the SQL warehouse, then ask questions in Chat and Agent mode.

---

# Part 1: Run the setup

## 1.1 What you need

- Databricks workspace with Genie and a SQL warehouse.
- In the notebook's top cells, set:
  - **CATALOG** – e.g. `humana_payer` (must already exist).
  - **SCHEMA** – e.g. `finance_revenue_tutorial` (created if it doesn't exist).
  - **WAREHOUSE_ID** – your SQL warehouse ID.

## 1.2 What the notebook creates

- Schema (if not exists), five tables, synthetic data, metric view `mv_financial_performance`, Genie space **Genie Room Tutorial - Finance & Revenue**, and `config_genie` with the space ID.
- The room is recreated each run (drop + create for this room only); other Genie rooms are untouched.

---

# Part 2: Data at a glance

Use this when writing instructions or SQL.

## 2.1 Tables (base schema)

- **membership_fact:** member_month_id, product_id, lob, region, period_month, member_months, enrollment_count, segment
- **revenue_fact:** revenue_id, product_id, lob, period_month, premium_revenue, other_revenue, total_revenue
- **mlr_fact:** mlr_id, product_id, lob, region, period_month, medical_cost, premium_revenue, mlr_pct
- **reserves_fact:** reserve_id, reserve_type, product_id, period_month, beginning_balance, ending_balance, reserve_movement
- **product_dim:** product_id, product_name, product_type, lob, active_flag

## 2.2 Metric view

- **mv_financial_performance**
  Dimensions: product_type, lob, region, period_month
  Measures: total_premium, total_revenue, total_medical_cost, mlr_pct_avg, member_months_total, pmpm_revenue

## 2.3 Metric views: what they are and how they're used in this room

**What metric views are**

Metric views are a Unity Catalog feature that define a **semantic layer** over your data: **dimensions** (attributes to group or filter by) and **measures** (aggregations like sums and averages). They are created with `CREATE VIEW ... WITH METRICS LANGUAGE YAML` and sit on top of a table or view. Genie (and other tools) can query them so users get consistent KPIs without writing the aggregation logic each time.

**How this Genie room uses the metric view**

- The notebook creates **mv_financial_performance** (section 3b), built on a join of **revenue_fact**, **mlr_fact**, and **membership_fact**. It exposes dimensions (product_type, lob, region, period_month) and measures (total_premium, total_revenue, total_medical_cost, mlr_pct_avg, member_months_total, pmpm_revenue).
- The Genie space **data sources** include both the five tables and this metric view. So Genie can choose either the raw tables or the metric view when answering.
- The room's **text instructions** tell Genie to prefer the metric view for "common KPIs and rollups." That steers Genie to use it when the question fits the metric view's dimensions and measures.

**Tables vs metric view in this room**

- **Use the tables** when the question needs: reserve-level detail (reserves_fact), product reference data (product_dim), specific enrollment segments (membership_fact.segment), or custom filters/columns that aren't in the metric view.
- **Use the metric view** when the question is about financial **KPIs** that match its dimensions and measures: revenue, premium, MLR, member months, or PMPM, grouped or filtered by product_type, lob, region, or period.

**What kind of queries use the metric view**

Queries that ask for aggregated financial performance by the metric view's dimensions. Examples:

- Total revenue or premium by product, LOB, region, or month.
- MLR percentage by LOB or region.
- Member months and PMPM by product type.
- Comparisons across regions or LOBs using those measures.

**Example natural-language questions that can use the metric view**

- "Revenue by product and month"
- "MLR by line of business"
- "Premium per member per month by region"
- "Total medical cost by LOB and quarter"
- "Member months trend by product type"

**Example SQL (what Genie might generate against the metric view)**

```sql
-- Revenue by LOB and month
SELECT lob, period_month, total_revenue, total_premium, mlr_pct_avg
FROM YOUR_CATALOG.YOUR_SCHEMA.mv_financial_performance
GROUP BY lob, period_month, total_revenue, total_premium, mlr_pct_avg;
```

Replace `YOUR_CATALOG.YOUR_SCHEMA` with your catalog and schema. In practice, Genie will generate the right aggregation based on the metric view's definition.

---

# Part 3: Configure the Genie room

In Databricks: **SQL → Genie** → open **Genie Room Tutorial - Finance & Revenue** → **Configure**.

## 3.1 Instructions → Text

Paste into **Instructions → Text** (replace YOUR_CATALOG.YOUR_SCHEMA in the text if you mention it):

```
You are querying Payer Finance & Revenue data for a US health plan. This space helps senior financial analysts, finance leaders, and actuarial teams explore premium revenue, medical loss ratio (MLR), membership, reserves, and financial trends.

Data Sources (YOUR_CATALOG.YOUR_SCHEMA):
- membership_fact: member_month_id, product_id, lob, region, period_month, member_months, enrollment_count, segment
- revenue_fact: revenue_id, product_id, lob, period_month, premium_revenue, other_revenue, total_revenue
- mlr_fact: mlr_id, product_id, lob, region, period_month, medical_cost, premium_revenue, mlr_pct
- reserves_fact: reserve_id, reserve_type, product_id, period_month, beginning_balance, ending_balance, reserve_movement
- product_dim: product_id, product_name, product_type, lob, active_flag
- Metric view mv_financial_performance: dimensions product_type, lob, region, period_month; measures total_premium, total_revenue, total_medical_cost, mlr_pct_avg, member_months_total, pmpm_revenue. Prefer metric view for common KPIs.

Key concepts:
- MLR = Medical Cost / Premium Revenue (lower is better for profitability)
- PMPM = Per Member Per Month (revenue or cost divided by member months)
- LOB = Line of Business (MA, PDP, MAPD, Commercial, Medicaid)
- Reserve movement = Ending Balance - Beginning Balance

Query guidelines:
(1) Revenue/premium: use revenue_fact or mv_financial_performance; join to product_dim for product names.
(2) MLR analysis: use mlr_fact or mv_financial_performance; can join to membership_fact for enrollment context.
(3) Membership/enrollment: use membership_fact; group by lob, region, segment, or period_month.
(4) Reserves: use reserves_fact; group by reserve_type, product_id, or period_month.
(5) Product lookup: join to product_dim on product_id for product_name and product_type.
(6) Time trends: use period_month for monthly analysis; use DATE_TRUNC for quarterly/yearly.

Response style: clear tables/charts; financial figures formatted with commas; percentages for MLR; rankings for top/bottom products or LOBs; no carrier or client names.
```

## 3.2 Instructions → Joins

**Instructions → Joins → + Add** for each join below (use full table names if the UI requires them).

**Join 1:** revenue_fact → product_dim
- **Condition:** `revenue_fact.product_id = product_dim.product_id`
- **Relationship type:** Many to One
- **Instructions:** Use when adding product names or types to revenue analysis.

**Join 2:** mlr_fact → product_dim
- **Condition:** `mlr_fact.product_id = product_dim.product_id`
- **Relationship type:** Many to One
- **Instructions:** Use when adding product details to MLR analysis.

**Join 3:** membership_fact → product_dim
- **Condition:** `membership_fact.product_id = product_dim.product_id`
- **Relationship type:** Many to One
- **Instructions:** Use when adding product names to membership analysis.

**Join 4:** reserves_fact → product_dim
- **Condition:** `reserves_fact.product_id = product_dim.product_id`
- **Relationship type:** Many to One
- **Instructions:** Use when adding product details to reserve analysis.

**Join 5:** revenue_fact → membership_fact
- **Condition:** `revenue_fact.product_id = membership_fact.product_id AND revenue_fact.lob = membership_fact.lob AND revenue_fact.period_month = membership_fact.period_month`
- **Relationship type:** Many to Many
- **Instructions:** Use when calculating PMPM or combining revenue with membership.

**Join 6:** mlr_fact → membership_fact
- **Condition:** `mlr_fact.product_id = membership_fact.product_id AND mlr_fact.lob = membership_fact.lob AND mlr_fact.region = membership_fact.region AND mlr_fact.period_month = membership_fact.period_month`
- **Relationship type:** Many to Many
- **Instructions:** Use when combining MLR with membership for cost per member analysis.

## 3.3 Instructions → SQL Expressions

**Instructions → SQL Expressions → + Add**. Choose **Measure**, **Filter**, or **Dimension** and fill in the fields.

**Measures**

- **mlr_calculated** (Tables: mlr_fact)
  Code: `ROUND(SUM(mlr_fact.medical_cost) * 100.0 / NULLIF(SUM(mlr_fact.premium_revenue), 0), 2)`
  Synonyms: medical loss ratio, loss ratio, cost ratio
  Instructions: Calculated MLR percentage from medical cost divided by premium revenue.

- **pmpm_revenue** (Tables: revenue_fact, membership_fact)
  Code: `ROUND(SUM(revenue_fact.total_revenue) / NULLIF(SUM(membership_fact.member_months), 0), 2)`
  Synonyms: revenue per member, per member per month, pmpm
  Instructions: Revenue divided by member months for PMPM calculation.

- **reserve_movement_total** (Tables: reserves_fact)
  Code: `SUM(reserves_fact.reserve_movement)`
  Synonyms: reserve change, reserve delta, movement
  Instructions: Total change in reserves over the period.

**Filters**

- **Medicare Advantage only** – Code: `product_dim.product_type = 'MA'` | Synonyms: MA, medicare advantage, MA only
- **Commercial only** – Code: `product_dim.product_type = 'Commercial'` | Synonyms: commercial, group, employer
- **Active products only** – Code: `product_dim.active_flag = true` | Synonyms: active, current products, in force
- **YTD** – Code: `membership_fact.period_month >= DATE_TRUNC('year', CURRENT_DATE)` | Synonyms: year to date, ytd, this year
- **Prior year** – Code: `membership_fact.period_month >= DATE_TRUNC('year', DATEADD(YEAR, -1, CURRENT_DATE)) AND membership_fact.period_month < DATE_TRUNC('year', CURRENT_DATE)` | Synonyms: last year, prior year, py

**Dimensions**

- **LOB** – Code: `revenue_fact.lob`
- **Product type** – Code: `product_dim.product_type`
- **Region** – Code: `membership_fact.region`
- **Period month** – Code: `revenue_fact.period_month`
- **Period quarter** – Code: `DATE_TRUNC('quarter', revenue_fact.period_month)`
- **Reserve type** – Code: `reserves_fact.reserve_type`

## 3.4 Instructions → SQL Queries (example queries)

Add via **+ Add** (replace YOUR_CATALOG.YOUR_SCHEMA):

**Revenue by product and month:**
```sql
SELECT p.product_name, p.product_type, r.period_month,
  SUM(r.premium_revenue) AS premium_revenue,
  SUM(r.other_revenue) AS other_revenue,
  SUM(r.total_revenue) AS total_revenue
FROM YOUR_CATALOG.YOUR_SCHEMA.revenue_fact r
JOIN YOUR_CATALOG.YOUR_SCHEMA.product_dim p ON r.product_id = p.product_id
GROUP BY p.product_name, p.product_type, r.period_month
ORDER BY r.period_month, total_revenue DESC
```

**MLR by line of business:**
```sql
SELECT lob,
  SUM(medical_cost) AS total_medical_cost,
  SUM(premium_revenue) AS total_premium,
  ROUND(SUM(medical_cost) * 100.0 / NULLIF(SUM(premium_revenue), 0), 2) AS mlr_pct
FROM YOUR_CATALOG.YOUR_SCHEMA.mlr_fact
GROUP BY lob
ORDER BY mlr_pct DESC
```

**Membership trend by product:**
```sql
SELECT p.product_name, m.period_month,
  SUM(m.member_months) AS member_months,
  SUM(m.enrollment_count) AS enrollment_count
FROM YOUR_CATALOG.YOUR_SCHEMA.membership_fact m
JOIN YOUR_CATALOG.YOUR_SCHEMA.product_dim p ON m.product_id = p.product_id
GROUP BY p.product_name, m.period_month
ORDER BY m.period_month, member_months DESC
```

**Reserve movement by quarter:**
```sql
SELECT reserve_type, DATE_TRUNC('quarter', period_month) AS quarter,
  SUM(beginning_balance) AS beginning_balance,
  SUM(ending_balance) AS ending_balance,
  SUM(reserve_movement) AS reserve_movement
FROM YOUR_CATALOG.YOUR_SCHEMA.reserves_fact
GROUP BY reserve_type, DATE_TRUNC('quarter', period_month)
ORDER BY quarter, reserve_type
```

**Premium per member per month by LOB:**
```sql
SELECT r.lob,
  SUM(r.total_revenue) AS total_revenue,
  SUM(m.member_months) AS member_months,
  ROUND(SUM(r.total_revenue) / NULLIF(SUM(m.member_months), 0), 2) AS pmpm
FROM YOUR_CATALOG.YOUR_SCHEMA.revenue_fact r
JOIN YOUR_CATALOG.YOUR_SCHEMA.membership_fact m
  ON r.product_id = m.product_id AND r.lob = m.lob AND r.period_month = m.period_month
GROUP BY r.lob
ORDER BY pmpm DESC
```

## 3.5 Parameterized queries (Trusted responses)

Add these under **Instructions → SQL Queries**. For any `LIMIT :limit_count`, set the parameter type to **Numeric/Integer**.

**Top products by revenue** – Parameter: limit_count (Numeric/Integer). Example to test: 5, 10, 20.
```sql
SELECT p.product_name, p.product_type, p.lob,
  SUM(r.total_revenue) AS total_revenue
FROM YOUR_CATALOG.YOUR_SCHEMA.revenue_fact r
JOIN YOUR_CATALOG.YOUR_SCHEMA.product_dim p ON r.product_id = p.product_id
GROUP BY p.product_name, p.product_type, p.lob
ORDER BY total_revenue DESC
LIMIT :limit_count
```

**MLR by LOB with region filter** – Parameter: region_filter (String, default ALL). Example: South, Midwest, Northeast, West, ALL.
```sql
SELECT m.lob, m.region,
  SUM(m.medical_cost) AS medical_cost,
  SUM(m.premium_revenue) AS premium_revenue,
  ROUND(SUM(m.medical_cost) * 100.0 / NULLIF(SUM(m.premium_revenue), 0), 2) AS mlr_pct
FROM YOUR_CATALOG.YOUR_SCHEMA.mlr_fact m
WHERE (:region_filter = 'ALL' OR m.region = :region_filter)
GROUP BY m.lob, m.region
ORDER BY mlr_pct DESC
```

**Reserves by type** – Parameter: reserve_type_filter (String). Example: IBNR, Premium Deficiency, Claim Liability.
```sql
SELECT reserve_type, period_month,
  beginning_balance, ending_balance, reserve_movement
FROM YOUR_CATALOG.YOUR_SCHEMA.reserves_fact
WHERE reserve_type = :reserve_type_filter
ORDER BY period_month
```

## 3.6 UDF (optional, for Trusted asset queries)

Run in SQL Editor or a notebook (replace YOUR_CATALOG.YOUR_SCHEMA), then add in Genie: **Configure → Add trusted asset → SQL Function**.

```sql
CREATE OR REPLACE FUNCTION YOUR_CATALOG.YOUR_SCHEMA.top_products_by_revenue(
  limit_count INT DEFAULT 10,
  lob_filter STRING DEFAULT NULL
)
RETURNS TABLE (
  product_name STRING,
  product_type STRING,
  lob STRING,
  total_revenue DOUBLE
)
COMMENT 'Returns top products by total revenue, optionally filtered by LOB.'
RETURN
  SELECT product_name, product_type, lob, total_revenue
  FROM (
    SELECT p.product_name, p.product_type, p.lob, SUM(r.total_revenue) AS total_revenue,
           ROW_NUMBER() OVER (ORDER BY SUM(r.total_revenue) DESC) AS rn
    FROM YOUR_CATALOG.YOUR_SCHEMA.revenue_fact r
    JOIN YOUR_CATALOG.YOUR_SCHEMA.product_dim p ON r.product_id = p.product_id
    WHERE (top_products_by_revenue.lob_filter IS NULL OR top_products_by_revenue.lob_filter = '' OR p.lob = top_products_by_revenue.lob_filter)
    GROUP BY p.product_name, p.product_type, p.lob
  ) ranked
  WHERE rn <= GREATEST(COALESCE(NULLIF(top_products_by_revenue.limit_count, 0), 10), 1);
```

## 3.7 Benchmarks (Benchmarks → Questions)

**+ Add benchmark** for each item below. **Question** = natural language; **Ground truth SQL** = replace YOUR_CATALOG.YOUR_SCHEMA in the SQL. Then click **Run all benchmarks** to compare Genie's answers to the ground truth.

**Question:** Revenue by product and month
**Ground truth SQL:**
```sql
SELECT p.product_name, p.product_type, r.period_month,
  SUM(r.total_revenue) AS total_revenue
FROM YOUR_CATALOG.YOUR_SCHEMA.revenue_fact r
JOIN YOUR_CATALOG.YOUR_SCHEMA.product_dim p ON r.product_id = p.product_id
GROUP BY p.product_name, p.product_type, r.period_month
ORDER BY r.period_month, total_revenue DESC
```

**Question:** MLR by line of business
**Ground truth SQL:**
```sql
SELECT lob,
  ROUND(SUM(medical_cost) * 100.0 / NULLIF(SUM(premium_revenue), 0), 2) AS mlr_pct
FROM YOUR_CATALOG.YOUR_SCHEMA.mlr_fact
GROUP BY lob
ORDER BY mlr_pct DESC
```

**Question:** Membership and premium trend by product
**Ground truth SQL:**
```sql
SELECT p.product_name, m.period_month,
  SUM(m.member_months) AS member_months,
  SUM(r.total_revenue) AS total_revenue
FROM YOUR_CATALOG.YOUR_SCHEMA.membership_fact m
JOIN YOUR_CATALOG.YOUR_SCHEMA.product_dim p ON m.product_id = p.product_id
JOIN YOUR_CATALOG.YOUR_SCHEMA.revenue_fact r ON m.product_id = r.product_id AND m.lob = r.lob AND m.period_month = r.period_month
GROUP BY p.product_name, m.period_month
ORDER BY m.period_month
```

**Question:** Reserve movement by quarter
**Ground truth SQL:**
```sql
SELECT reserve_type, DATE_TRUNC('quarter', period_month) AS quarter,
  SUM(reserve_movement) AS reserve_movement
FROM YOUR_CATALOG.YOUR_SCHEMA.reserves_fact
GROUP BY reserve_type, DATE_TRUNC('quarter', period_month)
ORDER BY quarter
```

**Question:** Premium per member per month by product
**Ground truth SQL:**
```sql
SELECT p.product_name,
  ROUND(SUM(r.total_revenue) / NULLIF(SUM(m.member_months), 0), 2) AS pmpm
FROM YOUR_CATALOG.YOUR_SCHEMA.revenue_fact r
JOIN YOUR_CATALOG.YOUR_SCHEMA.membership_fact m
  ON r.product_id = m.product_id AND r.lob = m.lob AND r.period_month = m.period_month
JOIN YOUR_CATALOG.YOUR_SCHEMA.product_dim p ON r.product_id = p.product_id
GROUP BY p.product_name
ORDER BY pmpm DESC
```

## 3.8 Settings

- **Description:** e.g. "Query payer finance and revenue metrics with natural language (tutorial)."
- **Sample questions:** Add e.g. "Revenue by product and month", "MLR by line of business", "Membership trend by product", "Reserve movement by quarter", "Premium per member per month by LOB".

---

# Part 4: Explore the room (step-by-step)

Use this section to **explore** the Genie room after setup and configuration. It walks through Chat, Agent mode, and a quick tour of Configure so you learn the room by doing.

## 4.1 Before you start

- The setup notebook has been run (schema, tables, data, Genie space exist).
- You have the SQL Warehouse ID set in the notebook and the warehouse is available.
- In Databricks: **SQL → Genie** → open **Genie Room Tutorial - Finance & Revenue**.

## 4.2 Start the SQL warehouse

1. If you see a banner like **"The SQL Warehouse … is stopped"**, click **Start Warehouse**.
2. Wait until the warehouse shows as running (green).
3. You can now ask questions in the Genie room.

## 4.3 Chat mode – basic questions

Stay in **Chat** mode and try these in order. Genie will turn them into SQL and return tables (and sometimes charts).

**3a – Revenue by product**

1. Type or click: **"Revenue by product and month"** or **"Top 10 products by revenue"**.
2. Submit.
3. You should see a table of products with revenue figures by period.
4. If you see a **Trusted** badge, Genie used a predefined query or UDF you added.

**3b – MLR analysis**

1. Ask: **"MLR by line of business"**.
2. You should see LOB, medical cost, premium, and MLR percentage.
3. MLR = (medical cost / premium) × 100.

**3c – Membership**

1. Ask: **"Membership trend by product"** or **"Member months by LOB and region"**.
2. You should see member months and enrollment counts over time or by dimension.

**3d – Reserves**

1. Ask: **"Reserve movement by quarter"**.
2. You should see reserve types with beginning balance, ending balance, and movement by quarter.

**Fallback:** If a question fails or returns empty, try **"Show me 10 rows from revenue_fact"** to confirm the room can query the tables.

### Questions that trigger the Trusted icon

After you add the **parameterized queries** and **UDF** (Part 3.5 and 3.6), these questions typically produce a **Trusted** badge when Genie uses the matching asset:

- **Top 10 products by revenue** → Parameterized "Top products" or UDF `top_products_by_revenue`
- **Top 5 products by revenue** → Parameterized "Top products" (limit_count = 5)
- **MLR by LOB in South region** → Parameterized "MLR by LOB with region filter" (region_filter = South)
- **IBNR reserves by month** → Parameterized "Reserves by type" (reserve_type_filter = IBNR)

## 4.4 Agent mode – analysis and visuals

Switch to **Agent** mode for multi-step analysis.

**Outliers**

1. In **Agent** mode, ask: **"Identify products or LOBs with unusually high or low MLR and potential causes"**.
2. The agent will analyze the data and point out outliers and possible reasons.

**Visualizations**

1. Ask: **"Visualize revenue trends by LOB over the last 12 months"**.
2. The agent may suggest and generate charts (e.g. line chart by LOB and month).

## 4.5 Configure tour – how the room is built

Click **Configure** (gear icon) to see how the room is set up. This is the same content you added in Part 3; here you're touring it.

- **Data:** Open the **Data** tab. You should see the five tables (and metric view if linked). These are the only data sources this Genie room can use.
- **Instructions → Text:** Domain text—what the data is, key concepts, and query guidelines (Part 3.1).
- **Instructions → Joins:** How tables relate (Part 3.2). Joins tell Genie how to write correct JOINs.
- **Instructions → SQL Queries:** Example and parameterized queries (Part 3.4, 3.5). Parameterized ones can be marked Trusted.
- **Settings:** Description and **Sample questions**.

## 4.6 Run benchmarks (optional)

1. Click **Benchmarks** in the Genie room.
2. Open the **Questions** tab.
3. If you haven't already, add benchmarks from Part 3.7 (question + ground truth SQL).
4. Click **Run all benchmarks** to see how often Genie's answers match the expected SQL/results.

---

# Part 5: Quick reference

## Quick reference – questions to try

| Question | Mode | What you get | Trusted? |
|----------|------|--------------|----------|
| Revenue by product and month | Chat | Revenue table by product and period | Maybe |
| Top 10 products by revenue | Chat | Top products ranked by revenue | Yes (if parameterized/UDF added) |
| MLR by line of business | Chat | LOB with MLR percentages | Maybe |
| MLR by LOB in South region | Chat | MLR filtered by South | Yes |
| Membership trend by product | Chat | Member months over time | Maybe |
| Reserve movement by quarter | Chat | Reserves by type and quarter | Maybe |
| IBNR reserves by month | Chat | IBNR reserve detail | Yes |
| Show me 10 rows from revenue_fact | Chat | Simple table check | No |
| Premium per member per month by LOB | Chat | PMPM by line of business | Maybe |
| Identify products with high MLR... | Agent | Outlier analysis | No |
| Visualize revenue trends... | Agent | Charts and summaries | No |

## Sample questions to add in Settings

Revenue by product and month • Top 10 products by revenue • MLR by line of business • Membership trend by product • Reserve movement by quarter • Premium per member per month by LOB • Show me 10 rows from revenue_fact

## Region and LOB values (for parameters)

- **Regions:** South, Midwest, Northeast, West (or ALL for no filter).
- **Lines of Business (LOB):** MA (Medicare Advantage), PDP (Prescription Drug Plan), MAPD (MA + PDP), Commercial, Medicaid.
- **Reserve Types:** IBNR, Premium Deficiency, Claim Liability.

## Key financial metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| MLR | Medical Cost / Premium Revenue | Lower is better for profitability; 80-85% typical |
| PMPM | Revenue (or Cost) / Member Months | Per member per month rate |
| Reserve Movement | Ending Balance - Beginning Balance | Positive = reserve increase |

## Next steps

- Use **Part 2 (Data at a glance)** when writing or debugging SQL and instructions.
- Add more sample questions based on your actual use cases.
- Tune the text instructions based on common questions from your finance team.
