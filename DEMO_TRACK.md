# Demo track — Genie: Payer Finance & Revenue

**Audience:** Live presentation (~8–10 minutes); **§0** = four Instructions tabs + call script; **§2** = **metric views** (UC semantic layer); **§6** = Instructions deep-dive and healthcare walkthrough; **§7–§10** = copy-paste reference and operations.  
**Prereqs:** Notebook has been run; Genie space **Genie Room Tutorial - Finance & Revenue** exists; SQL warehouse started.  
**Full setup:** See [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) and [README.md](README.md).

Replace `YOUR_CATALOG.YOUR_SCHEMA` everywhere below with your catalog and schema (e.g. `humana_payer.finance_revenue_tutorial`).

**MLR (Medical Loss Ratio):** medical cost relative to premium revenue—how much of the premium dollar goes to medical spend; a core payer finance KPI (lower is often better for underwriting margin).

**PMPM (Per Member Per Month):** a rate “per member per month”—typically revenue, premium, or cost **divided by member months** so you can compare across groups and time fairly.

**Tip:** Optional: start with **§0** (four tabs + one-liner) if the room is technical. **§2** explains **metric views** (UC semantic layer) vs base tables. Run **§1–§5** for the live demo. Use **§6** for Instructions tabs in depth and **§7–§10** for reference and operations.

---

## 0. The four Instructions areas (at-a-glance)

Under **SQL → Genie → [space] → Configure**, you mainly tune four **Instructions** tabs—plus **Benchmarks** for quality checks (§9).

| Tab | What you put there | Why it matters |
|-----|-------------------|----------------|
| **Text** | Business context, vocabulary (“MLR (Medical Loss Ratio),” “LOB,” “member months”), column hints, response style | Improves **intent detection** so questions map to the right tables and fields |
| **Joins** | Canonical join paths: keys, **cardinality**, when a join is “safe” | Genie **reuses** these instead of guessing joins every time—fewer wrong or exploding queries |
| **SQL Expressions** | **MEASURE**, **FILTER**, and **DIMENSION** rows (the tab in most screenshots) | Codifies **reusable business logic**—metrics, canned slices, grouping fields |
| **SQL Queries** | Full hand-written **SQL templates** (plain or **parameterized**) | Complex patterns, regulatory-style logic, or **locked-down** queries Genie can match or run as **Trusted** |

**Presenter note:** On **SQL Expressions**, each row is a named fragment Genie can inject into generated SQL. That tab is your **lightweight semantic layer** on top of Unity Catalog tables and metric views.

### How to explain it on a call (~30 seconds)

**Say:**

> “Genie has a **semantic configuration** where we teach it our language and rules: **Text** for business descriptions and vocabulary; **Joins** for safe relationships between tables; **SQL Expressions** for reusable **measures**, **filters**, and **dimensions**; and **SQL Queries** for full curated templates—including parameterized or governed reports. Once that’s configured, analysts ask in English and Genie maps to **our** definitions instead of inventing SQL on the fly.”

**Optional finance add-on:** “So metrics like **MLR (Medical Loss Ratio)** and **PMPM (Per Member Per Month)** always follow **our** formulas, not a one-off `SUM`/`GROUP BY` each time.”

**Then (optional):** Open **Configure** and click through **Text → Joins → SQL Expressions → SQL Queries** in 10 seconds each while narrating.

---

## 1. Open (30–45 seconds)

**Say:** Finance and actuarial teams often rely on spreadsheets and one-off SQL. Genie sits on **governed** data; we layer **metric views** plus the four **Instructions** tabs (§0) so answers use **our** MLR (Medical Loss Ratio), PMPM (Per Member Per Month), and join paths—not one-off guesses.

**Do:** Databricks → **SQL → Genie** → open **Genie Room Tutorial - Finance & Revenue**. Confirm the warehouse is running.

---

## 2. What’s under the hood (30 seconds — skip if short on time)

**Say:** This room uses payer-style facts: revenue, MLR (Medical Loss Ratio), membership, reserves, plus **product_dim**. The notebook created **mv_financial_performance** for standard measures (premium, revenue, medical cost, MLR (Medical Loss Ratio), member months, PMPM (Per Member Per Month)) and dimensions (product type, LOB, region, period).

**For technical viewers:** Instructions tell Genie to prefer the metric view for common KPI rollups and to use base tables for reserves, segments, and cuts that aren’t on the metric view.

### Metric views — what they are (talk track + detail)

**One-liner for the room:** “A **metric view** is Unity Catalog’s way of publishing a **semantic layer**: approved **dimensions** (how we slice) and **measures** (how we aggregate)—so Genie and SQL users hit **one definition** of revenue, MLR (Medical Loss Ratio), and PMPM (Per Member Per Month) instead of rewriting `SUM`/`GROUP BY` every time.”

**What they are:** In Databricks, **metric views** are UC objects (defined with `CREATE VIEW … WITH METRICS LANGUAGE YAML`) that sit on top of tables or views. They declare:

- **Dimensions** — attributes to **group or filter** by (e.g. product type, LOB, region, month).
- **Measures** — **aggregated metrics** (sums, averages, ratios) that the platform knows how to roll up consistently.

BI tools and Genie can query them like a table, but the **logic** for “what counts as total revenue” or “how MLR (Medical Loss Ratio) is computed” lives in the view definition—not in each analyst’s ad hoc SQL.

**This tutorial’s view — `mv_financial_performance`**

- **Built from:** joins across **revenue_fact**, **mlr_fact**, and **membership_fact** (see notebook / [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §2.2–2.3).
- **Dimensions:** `product_type`, `lob`, `region`, `period_month`.
- **Measures:** e.g. `total_premium`, `total_revenue`, `total_medical_cost`, `mlr_pct_avg`, `member_months_total`, `pmpm_revenue`.

The Genie space **data sources** include **both** the five base tables **and** this metric view, so Genie can pick the right grain.

**When Genie should use the metric view vs base tables**

| Use **mv_financial_performance** | Use **base tables** (and joins / expressions) |
|----------------------------------|-----------------------------------------------|
| KPI rollups that fit the view’s dimensions and measures: revenue, premium, MLR (Medical Loss Ratio), member months, PMPM (Per Member Per Month) by product type, LOB, region, period | **Reserves** (`reserves_fact`), **product names** via **product_dim**, **segment** or other columns **not** on the metric view, or highly custom logic |
| Questions like “revenue by LOB and month,” “MLR (Medical Loss Ratio) by region,” “PMPM (Per Member Per Month) by product type” | “Reserve movement by quarter,” “enrollment by segment,” joins that need extra attributes |

**Text instructions** in this room tell Genie to **prefer the metric view** for those common financial KPIs; that nudges generation toward governed measures when the question matches.

**Optional SQL shape (illustrative):** Genie may emit queries similar to selecting dimensions and measures from `YOUR_CATALOG.YOUR_SCHEMA.mv_financial_performance` with appropriate `GROUP BY`—see [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §2.3 for a short example.

**How this fits with SQL Expressions:** **Metric views** lock in **dataset-level** semantics in UC. **SQL Expressions** in Genie add **room-level** named fragments (extra measures, filters, dimensions) and work alongside tables *and* the metric view. Together: UC metric view for consistent KPIs; Genie instructions for vocabulary, joins, and extra business rules.

---

## 3. Live questions (pick 4–5; ~1–1.5 min each)

| Order | Ask in Chat | What you’re showing |
|-------|-------------|---------------------|
| 1 | Revenue by product and month | NL → SQL, table/chart |
| 2 | MLR (Medical Loss Ratio) by line of business | Core finance metric, rankings |
| 3 | PMPM (Per Member Per Month) by LOB — *or ask “premium per member per month by LOB”* | Revenue + membership logic |
| 4 | Reserve movement by quarter | Reserves path (not only metric view) |
| 5 | Top 5 products by revenue | Optional: parameterized / trusted queries if configured |

If you demo **Agent mode**, use the same questions; mention multi-step behavior only if your room is set up for it.

**Trusted badge (if configured):** Call out when Genie uses a saved query or UDF—e.g. *Top 10 products by revenue*, *MLR (Medical Loss Ratio) by LOB in South region*, *IBNR reserves by month*. See [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §4.3.

---

## 4. How it’s built (45 seconds — if asked)

**Say:** We tuned Genie the same way we’d document a semantic layer: the Genie space includes Unity Catalog’s **metric view** `mv_financial_performance` as a **data source** (§2) plus the five tables. Then **Text** (who’s asking, what MLR (Medical Loss Ratio) / PMPM (Per Member Per Month) mean, when to prefer the metric view), **Joins** (canonical paths—e.g. `membership_fact` → `product_dim` on `product_id`; revenue ↔ membership for PMPM (Per Member Per Month)), **SQL Expressions** (named measures, filters, dimensions), and **SQL Queries** (full patterns and optional parameters for trusted templates). **Benchmarks** regression-test after changes.

**Do:** **Configure** → walk the four **Instructions** tabs in order, then **Benchmarks** if relevant. Avoid live pasting long SQL unless someone asks.

---

## 5. Close (20 seconds)

**Say:** The pattern generalizes: **governed data** + **metric views** + the four **Instructions** tabs (§0) gives finance users repeatable answers. **Benchmarks** catch drift after changes; **monitoring** (§10) covers warehouse health and spot checks.

**Offer:** Follow up on notebook deploy, UC, or production hardening as needed.

---

## 6. What each Instructions tab does (concepts)

Use this section when someone asks **how** Genie is configured. It matches the four tabs under **Configure → Instructions**, plus validation and trusted assets.

### 1. Text

**What it is:** Plain-language description of the dataset and how your business talks about it: what “member,” “enrollment,” “LOB,” “MLR (Medical Loss Ratio),” “PMPM (Per Member Per Month),” and “reserve movement” mean; typical questions users ask; tables and columns Genie should prefer; terms to **avoid** or **prefer**; formatting (percentages, commas).

**What it does:** Improves **intent detection** so natural language maps to the **right tables and fields** before SQL is generated. Text does **not** execute SQL—it steers the model.

### 2. Joins

**What it is:** **Canonical join paths**: which keys link tables, **cardinality** (many-to-one vs many-to-many), and short guidance on when to use each join.

**What it does:** You teach Genie the safe paths **once** (e.g. `membership_fact` → `product_dim` on `product_id`). It reuses those definitions whenever it needs to combine tables, instead of guessing joins on every question—reducing wrong joins and **row explosion**. PMPM (Per Member Per Month) questions rely on explicit **revenue_fact ↔ membership_fact** keys plus **period_month** and **LOB** alignment.

### 3. SQL Expressions (the tab in most screenshots)

**What it is:** Reusable **business logic** as named SQL fragments—still under **Instructions → SQL Expressions**.

**MEASURE** rows define **metrics** over facts, e.g. MLR (Medical Loss Ratio) and PMPM (Per Member Per Month) in *this* tutorial:

- **`mlr_calculated`** (on `mlr_fact`):  
  `ROUND(SUM(mlr_fact.medical_cost) * 100.0 / NULLIF(SUM(mlr_fact.premium_revenue), 0), 2)`  
  Genie can use this when users say “MLR (Medical Loss Ratio)” or “medical loss ratio” instead of re-deriving a different formula. *(Use **premium_revenue** here—this room’s `mlr_fact` doesn’t use `total_revenue` for the ratio.)*

- **`pmpm_revenue`** (on `revenue_fact` + `membership_fact`): **PMPM (Per Member Per Month)** = revenue ÷ member months (see §7 for full expression).

**FILTER** rows are **canned predicates**—like a saved `WHERE` clause:

- e.g. **Medicare Advantage only:** `product_dim.product_type = 'MA'`
- **YTD:** `membership_fact.period_month >= DATE_TRUNC('year', CURRENT_DATE)`  
  Genie can apply these when users say “for MA,” “commercial only,” or “year to date.”

**DIMENSION** rows declare **grouping** fields (and derived time grains): LOB, product type, region, `period_month`, quarter via `DATE_TRUNC`, reserve type, etc. Genie uses them for “**by** LOB,” “**by** region,” “**by** quarter.”

**Together:** Measures + filters + dimensions form a **semantic layer** Genie injects into generated SQL for **consistent** KPIs and slices.

**How they combine in one question**

- User: “**MLR (Medical Loss Ratio) for Medicare Advantage by region last year**”  
  - **Filters:** MA + prior year  
  - **Dimensions:** region (and time if needed)  
  - **Measure:** `mlr_calculated`  

### 4. SQL Queries

**What it is:** **Full, hand-written SQL** you save under **Instructions → SQL Queries**: joins, `GROUP BY`, optional `ORDER BY`, full three-part names.

**What it does:** For **complex** patterns—multi-fact logic, regulatory-style layouts, or rules that are hard to capture in fragments alone—Genie can **start from** or **match** your curated SQL instead of generating from scratch. Plain examples teach **shape**; see below for **parameterized** templates.

#### Parameterized queries (still under SQL Queries)

**What it is:** The same as above, but with **placeholders** (`:limit_count`, `:region_filter`, `:reserve_type_filter`, …) and typed parameters in the UI.

**What it does:** Genie **binds** values from the question (e.g. top **5**, **South** region). When intent matches, it may run **that exact template**—often **Trusted**—so variability (N, region, reserve type) stays inside **approved** SQL.

**Contrast:** **SQL Expressions** = reusable **fragments**. **SQL Queries** = **whole statements** (patterns or locked templates).

### Benchmarks (separate area from the four tabs)

**What they are:** **Question** + **ground truth SQL** pairs.

**What they do:** **Regression testing** after you change Text, Joins, Expressions, Queries, or data. They do not change runtime behavior for users. Details: §9.

### Trusted assets (SQL functions / UDFs)

**What it is:** Unity Catalog **SQL functions** registered as trusted assets.

**What it does:** Packages logic you want invoked as a single call—complement to parameterized **SQL Queries**. See [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §3.6.

---

### Concrete healthcare example: MLR (Medical Loss Ratio), PMPM (Per Member Per Month), MA vs Commercial (all four tabs)

Walk this if someone asks for an **end-to-end** picture of how the same concepts appear across tabs.

| Tab | What you configure for this tutorial |
|-----|--------------------------------------|
| **Text** | Payer finance context; define **MLR (Medical Loss Ratio)**, **PMPM (Per Member Per Month)**, **LOB**; list `membership_fact`, `revenue_fact`, `mlr_fact`, `reserves_fact`, `product_dim`, and **mv_financial_performance**; instruct Genie to **prefer the metric view** for common KPI rollups. |
| **Joins** | Facts to **product_dim**; **revenue_fact** to **membership_fact** on `product_id`, `lob`, `period_month` (for PMPM (Per Member Per Month)); **mlr_fact** to **membership_fact** when combining MLR (Medical Loss Ratio) with enrollment. |
| **SQL Expressions** | **MEASURE:** `mlr_calculated`, `pmpm_revenue`, `reserve_movement_total`. **FILTER:** MA only, Commercial only, Active products, YTD, Prior year. **DIMENSION:** LOB, product type, region, month, quarter, reserve type. |
| **SQL Queries** | Example **PMPM (Per Member Per Month) by LOB** and **MLR (Medical Loss Ratio) by LOB** full SQL (§8 / complete guide §3.4); optional **parameterized** top-N, region slice, reserves-by-type (§8 / §3.5). |

**Outside the four tabs:** The Genie space **data sources** also include the UC **metric view** `mv_financial_performance` (§2). That is where governed KPI dimensions/measures are defined in the catalog; **Text** + **SQL Expressions** steer *when* Genie uses the view vs raw facts.

**Demo question tying it together:** *“Show MLR (Medical Loss Ratio) by LOB for Medicare Advantage year to date.”* — Text interprets intent; Joins connect `mlr_fact` to `product_dim`; Expressions supply the **MA** filter, **YTD** filter, **LOB** dimension, and **mlr_calculated** measure; if you added a matching **SQL Query**, Genie might use it as a **Trusted** template.

---

## 7. SQL expressions (reference)

Add under **Configure → Instructions → SQL Expressions → + Add**. Pick type **Measure**, **Filter**, or **Dimension** and attach the listed tables. **What these are for:** see §6 (Measures / Filters / Dimensions).

**Demo line:** “These are reusable building blocks—Genie maps natural language like ‘MA only’ or ‘PMPM (Per Member Per Month)’ to vetted SQL.”

### Measures

| Name | Tables | Code | Synonyms (examples) |
|------|--------|------|---------------------|
| **mlr_calculated** | mlr_fact | `ROUND(SUM(mlr_fact.medical_cost) * 100.0 / NULLIF(SUM(mlr_fact.premium_revenue), 0), 2)` | medical loss ratio, loss ratio, cost ratio |
| **pmpm_revenue** | revenue_fact, membership_fact | `ROUND(SUM(revenue_fact.total_revenue) / NULLIF(SUM(membership_fact.member_months), 0), 2)` | revenue per member per month, PMPM (Per Member Per Month), pmpm |
| **reserve_movement_total** | reserves_fact | `SUM(reserves_fact.reserve_movement)` | reserve change, reserve delta, movement |

### Filters

| Name | Code | Synonyms (examples) |
|------|------|---------------------|
| Medicare Advantage only | `product_dim.product_type = 'MA'` | MA, medicare advantage, MA only |
| Commercial only | `product_dim.product_type = 'Commercial'` | commercial, group, employer |
| Active products only | `product_dim.active_flag = true` | active, current products, in force |
| YTD | `membership_fact.period_month >= DATE_TRUNC('year', CURRENT_DATE)` | year to date, ytd, this year |
| Prior year | `membership_fact.period_month >= DATE_TRUNC('year', DATEADD(YEAR, -1, CURRENT_DATE)) AND membership_fact.period_month < DATE_TRUNC('year', CURRENT_DATE)` | last year, prior year, py |

### Dimensions

| Name | Code |
|------|------|
| LOB | `revenue_fact.lob` |
| Product type | `product_dim.product_type` |
| Region | `membership_fact.region` |
| Period month | `revenue_fact.period_month` |
| Period quarter | `DATE_TRUNC('quarter', revenue_fact.period_month)` |
| Reserve type | `reserves_fact.reserve_type` |

Full copy-paste blocks and UI notes: [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §3.3.

---

## 8. Example SQL & parameterized queries (reference)

Add under **Configure → Instructions → SQL Queries** via **+ Add**. **Roles:** example SQL = **pattern / reference** for generation; parameterized SQL = **fixed template** with slots Genie fills (often **Trusted**). See §6.

**Demo line:** “Golden examples teach Genie our join keys and aggregations; parameterized queries power governed ‘top N’ and slice-by-region answers.”

### Example queries (non-parameterized)

| Purpose | One-line description |
|---------|----------------------|
| Revenue by product and month | `revenue_fact` + `product_dim`; sums premium, other, total revenue by period |
| MLR (Medical Loss Ratio) by line of business | `mlr_fact`; aggregated MLR % by LOB |
| Membership trend by product | `membership_fact` + `product_dim`; member months and enrollment over time |
| Reserve movement by quarter | `reserves_fact`; balances and movement by quarter |
| PMPM (Per Member Per Month) by LOB | `revenue_fact` + `membership_fact` on product, LOB, period_month |

Full SQL for each: [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §3.4.

### Parameterized queries (trusted responses)

| Query | Parameters | Example test values |
|-------|------------|----------------------|
| Top products by revenue | `limit_count` (Numeric/Integer) | 5, 10, 20 |
| MLR (Medical Loss Ratio) by LOB with region filter | `region_filter` (String; default ALL) | South, Midwest, Northeast, West, ALL |
| Reserves by type | `reserve_type_filter` (String) | IBNR, Premium Deficiency, Claim Liability |

For `LIMIT :limit_count`, set the parameter type to **Numeric/Integer** in the UI. Full SQL: [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §3.5.

### Optional: trusted SQL function (UDF)

The guide includes `top_products_by_revenue(limit_count, lob_filter)` for **Configure → Add trusted asset → SQL Function**. Use when you want Genie to call a UC function instead of ad hoc SQL. See [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §3.6.

---

## 9. Benchmarks (talk track + checklist)

**Where:** **Configure → Benchmarks → Questions** (wording may appear as **Benchmarks** in the Genie space settings). **Purpose:** see §6.

**Say:** “Benchmarks pair a natural-language **question** with **ground truth SQL**. After we change instructions, joins, or data, we **Run all benchmarks** and compare Genie’s generated SQL and results to the expected query—cheap regression testing for a critical room.”

### Benchmark questions in this tutorial

| # | Question (natural language) | What it validates |
|---|----------------------------|-------------------|
| 1 | Revenue by product and month | Revenue + product join, time grain |
| 2 | MLR (Medical Loss Ratio) by line of business | MLR (Medical Loss Ratio) aggregation by LOB |
| 3 | Membership and premium trend by product | Multi-fact join (membership + revenue + product) |
| 4 | Reserve movement by quarter | Reserves + quarterly truncation |
| 5 | PMPM (Per Member Per Month) by product — *or “premium per member per month by product”* | PMPM (Per Member Per Month) with revenue + membership + product |

**Ground truth SQL** for each benchmark is in [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) §3.7—paste into each benchmark’s **Ground truth SQL** field after replacing catalog/schema.

### Checklist

- [ ] Every benchmark has **Question** + **Ground truth SQL** with correct `YOUR_CATALOG.YOUR_SCHEMA`.
- [ ] Run **Run all benchmarks** after initial configuration.
- [ ] Re-run after any change to: text instructions, joins, SQL expressions, added/removed tables or metric view, or major data refresh.
- [ ] Investigate failures: wrong table choice (fact vs metric view), missing join, or ambiguous wording—tighten instructions or add an example query.

---

## 10. Monitoring & operations

Genie does not replace full observability; treat **benchmarks** as your functional tests and add **platform** checks below.

### Quality and regression

- **Benchmark cadence:** Run all benchmarks after deploys to the room config and after schema or metric view changes.
- **Spot checks:** Periodically ask 2–3 “golden” questions from §3 in Chat and confirm numbers match a known SQL snapshot or dashboard.
- **Failed answers:** When users report bad answers, capture the question and either add a benchmark or an example SQL query so the behavior is locked in.

### Warehouse and performance

- Ensure the Genie-attached **SQL warehouse** is rightsized; stopped warehouses cause user-visible delays on first question.
- Use **query history** (warehouse / SQL UI) to inspect slow or failing Genie-generated SQL and tune tables or warehouse size if needed.

### Governance (Unity Catalog)

- **Lineage and access:** Confirm analysts have only the catalog/schema privileges you intend; changes to underlying tables affect Genie answers—coordinate with data owners.
- **Audit:** Where your org uses UC audit or system tables, include Genie-critical schemas in access reviews and change control.

### Optional: analytics at scale

If your workspace exposes **usage or Genie analytics** (product-dependent), use them for adoption and top questions; pair with benchmarks for **correctness**, not just volume.

---

## Backup if Genie misbehaves

- Retry a simpler prompt: *MLR (Medical Loss Ratio) by line of business* or *Revenue by product and month*.
- Or run the matching example SQL from [GENIE_ROOM_COMPLETE_GUIDE.md](GENIE_ROOM_COMPLETE_GUIDE.md) in the SQL editor and note that Genie automates this class of query.
- Verify catalog, schema, and warehouse match the notebook configuration.
- Re-run **benchmarks** (§9) to see which golden questions fail and narrow the misconfiguration.
