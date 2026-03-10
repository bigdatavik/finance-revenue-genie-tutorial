# Finance & Revenue Genie Tutorial

A **deploy-only** Genie Room setup for **Payer Finance & Revenue** analytics. Use the Databricks Asset Bundle to deploy the job to your workspace; the job is **not run** by the bundle. You run the notebook once manually, then complete the room using the included guide.

---

## What's in this repo

| File | Purpose |
|------|---------|
| **One_Notebook_Genie_Room_Setup.py** | Single notebook: creates schema (if needed), tables, synthetic data, metric views, and Genie space. Edit `CATALOG`, `SCHEMA`, and `WAREHOUSE_ID` in the top cells before running. |
| **GENIE_ROOM_COMPLETE_GUIDE.md** | Full guide: setup, data reference, and how to configure the Genie room (Instructions, Joins, SQL Expressions, Queries, Trusted assets, Benchmarks). Use after running the notebook. |
| **databricks.yml.example** | Template for bundle config. Copy to `databricks.yml`, set your workspace host and profile; `databricks.yml` is gitignored. |

---

## Domain: Payer Finance & Revenue

This Genie room supports **senior financial analytics professionals** at a US health plan (e.g., Humana) with:

- **Premium and revenue:** Membership-based premium, other revenue, revenue by product and line of business
- **Medical loss ratio (MLR):** Claims cost, medical expense, and MLR by product, region, and time
- **Membership:** Enrollment counts, membership trend, segment and product mix
- **Reserves:** Reserve positions, reserve movement by quarter or period
- **Variance and trend analysis:** Supporting explanation of variances and trends for planning, forecasting, and senior management reporting

---

## Tables and Schema

| Table | Description | Grain |
|-------|-------------|-------|
| **membership_fact** | Member months and enrollment counts | product-LOB-region-period |
| **revenue_fact** | Premium revenue and other revenue | product-LOB-period |
| **mlr_fact** | Medical cost and MLR calculations | product-LOB-region-period |
| **reserves_fact** | Reserve balances and movements | reserve_type-product-period |
| **product_dim** | Product and line of business reference | product_id |

### Metric View

- **mv_financial_performance**: Dimensions (product_type, lob, region, period_month); Measures (total_premium, total_revenue, total_medical_cost, mlr_pct, member_months, pmpm_revenue)

---

## Sample Questions

- "Revenue by product and month?"
- "MLR by line of business and quarter?"
- "Membership and premium trend by product?"
- "Reserve movement by quarter?"
- "What is the variance in medical cost by region versus prior period?"
- "Member months by LOB and region for the last 12 months?"
- "Premium per member per month by product?"
- "Top products by revenue?"
- "Which LOB has the highest MLR?"

---

## Requirements

- Databricks workspace with Genie and Unity Catalog
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) installed
- SQL warehouse for the Genie space
- **Catalog must already exist** — do not create a catalog. Use your existing catalog (e.g. for staging/fevm, use **humana_payer**). The notebook only creates or uses a schema inside that catalog.

---

## Step-by-step: deploy and run the Genie room

### Step 1: Clone or copy this folder

```bash
cd ~/finance_revenue_genie_tutorial
```

### Step 2: Authenticate the Databricks CLI

```bash
databricks auth login --profile fevm
```

Complete the browser login.

### Step 3: Edit the notebook config (before first run)

Open **One_Notebook_Genie_Room_Setup.py** and set in the top cells:

- **CATALOG** — Your existing Unity Catalog name. **Do not create a new catalog.** For staging (fevm) use **humana_payer**.
- **SCHEMA** — Schema name for this Genie room (e.g. `finance_revenue_tutorial`). The notebook will create it if it does not exist.
- **WAREHOUSE_ID** — Your SQL warehouse ID (Databricks → SQL Warehouses → copy ID).

### Step 4: Bundle config (first time only)

Copy the example config and set your workspace details (do not commit `databricks.yml`):

```bash
cp databricks.yml.example databricks.yml
# Edit databricks.yml: set workspace.host, workspace.profile, and targets.staging.workspace.host/profile
```

### Step 5: Deploy the bundle (job is not run)

From the repo root:

```bash
databricks bundle deploy --target staging --profile YOUR_PROFILE
```

This uploads the notebook and creates the job (e.g. **genie_room_setup_staging**) in the workspace. The job is **not** run automatically.

### Step 6: Run the job once in Databricks

- Go to **Workflows → Jobs** in the Databricks workspace.
- Open the job (e.g. **finance_revenue_genie_room_setup_staging**) and click **Run now**.

Or open the notebook **One_Notebook_Genie_Room_Setup.py** in the workspace and run it there.

The notebook will: use your catalog, create the schema if needed, create tables, seed data, create the metric view, and create the Genie space.

### Step 7: Complete the Genie room

Use **[GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md)** to:

- Configure **Instructions**, **Joins**, **SQL Expressions**, **Queries**, **Trusted assets**, **Benchmarks**.
- Replace `YOUR_CATALOG.YOUR_SCHEMA` in the guide with your catalog and schema (e.g. `humana_payer.finance_revenue_tutorial`).
- Explore the room and refine sample questions.

---

## Quick reference

| Step | Command or action |
|------|-------------------|
| 1. Navigate | `cd ~/finance_revenue_genie_tutorial` |
| 2. Auth | `databricks auth login --profile fevm` |
| 3. Notebook | Edit `CATALOG`, `SCHEMA`, `WAREHOUSE_ID` in **One_Notebook_Genie_Room_Setup.py** (catalog = existing, e.g. humana_payer) |
| 4. Config | `cp databricks.yml.example databricks.yml` and edit host/profile |
| 5. Deploy | `databricks bundle deploy --target staging --profile YOUR_PROFILE` (job not run) |
| 6. Run job | In Databricks: Workflows → Jobs → run **finance_revenue_genie_room_setup_staging** (or run the notebook) |
| 7. Configure room | Follow **GENIE_ROOM_COMPLETE_GUIDE.md** |
