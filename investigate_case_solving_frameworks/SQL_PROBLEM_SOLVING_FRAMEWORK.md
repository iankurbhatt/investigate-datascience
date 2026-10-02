# 🧠 The Universal SQL Problem-Solving Framework

> A battle-tested mental model and execution blueprint for solving business cases and technical interview questions using **SQL**.

---

## 📑 Table of Contents
1. [The 4-Step Reverse Engineering Blueprint](#1-the-4-step-reverse-engineering-blueprint)
2. [Step 1: Target Output Contract (Start with the Destination)](#step-1-target-output-contract-start-with-the-destination)
3. [Step 2: Raw Schema & Cardinality Audit](#step-2-raw-schema--cardinality-audit)
4. [Step 3: The 4-Block Modular CTE Pipeline](#step-3-the-4-block-modular-cte-pipeline)
   - [Blueprint 1: Segment Aggregations & Conditional Logic](#blueprint-1-segment-aggregations--conditional-logic)
   - [Blueprint 2: Relational Joins & Safe Anti-Joins](#blueprint-2-relational-joins--safe-anti-joins)
   - [Blueprint 3: Window Functions & Time-Series Analytics](#blueprint-3-window-functions--time-series-analytics)
   - [Blueprint 4: Top-N & Ranking per Group](#blueprint-4-top-n--ranking-per-group)
   - [Blueprint 5: The Fast 2-Block Live Interview Alternative](#blueprint-5-the-fast-2-block-live-interview-alternative)
5. [Step 4: Defensive SQL & Sanity Verification](#step-4-defensive-sql--sanity-verification)
6. [SQL Execution Order vs Writing Order](#sql-execution-order-vs-writing-order)
7. [Business Request to SQL Translation Cheat Sheet](#business-request-to-sql-translation-cheat-sheet)

---

## 1. The 4-Step Reverse Engineering Blueprint

Always work backwards from what the stakeholder wants to see:

```
┌────────────────────────────────────────────────────────┐
│ STEP 1: TARGET OUTPUT (The Destination)                │
│ • What columns and metrics are required?               │
│ • What does exactly 1 row represent (Target Grain)?    │
│ • What is the final presentation? (Top-N / Ordering)   │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 2: RAW SCHEMA AUDIT (The Starting Point)          │
│ • Which tables contain the raw columns?                │
│ • Identify quirks: Nulls, string types, join keys      │
│ • Audit join cardinality: Avoid 1:N row duplication    │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 3: BACKWARD CTE TRANSFORMATION PIPELINE (Bridge)  │
│ • CTE 1: Cast Types ➔ Filter Early ➔ Strip Dates       │
│ • CTE 2: Pre-Aggregate Secondary Tables to 1:1 Grain   │
│ • CTE 3: Join Tables ➔ Window Functions ➔ Row Math     │
│ • Final SELECT: Group by Target Grain ➔ Aggregate      │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 4: SANITY AUDIT & VERIFICATION (The Guarantee)    │
│ • Guard against 0-division using NULLIF(col, 0)        │
│ • Prevent NULL propagation with COALESCE(col, default) │
│ • Assert Grain Uniqueness with COUNT(*) vs COUNT(DIST) │
└────────────────────────────────────────────────────────┘
```

---

## Step 1: Target Output Contract (Start with the Destination)

### 1.1 Target Schema & Metrics
- **Dimensions (Group Keys):** Categorical buckets (`account_tier`, `region`, `merchant_category`).
- **Aggregates:** Numerical sums and counts (`SUM(amount)`, `COUNT(DISTINCT customer_id)`).
- **Derived Ratios:** Business KPIs (`SUM(fraud_vol) / NULLIF(SUM(total_vol), 0) * 100`).

### 1.2 Target Grain
Ask: *"What does **exactly ONE row** represent in the output?"*
- 1 row per Customer -> `GROUP BY customer_id`
- 1 row per Region x Tier -> `GROUP BY region, account_tier`
- 1 row per Day -> `GROUP BY DATE(transaction_date)`

---

## Step 2: Raw Schema & Cardinality Audit

1. **Type Sanitization:**
   - Raw numeric strings: `CAST(amount AS REAL)`
   - Timestamps to dates: `DATE(transaction_date)`
   - Strings with whitespace: `LOWER(TRIM(status))`
2. **Cardinality Audit (Join Safety):**
   - If Table A has transactions and Table B has daily FX rates, **pre-aggregate Table B to 1 row per date** before joining to prevent 1:N row duplication!

---

## Step 3: The 4-Block Modular CTE Pipeline

```sql
WITH 
-- Block 1: Clean and filter primary fact table
cte_fact AS (
    SELECT 
        CAST(customer_id AS INTEGER) AS customer_id,
        DATE(transaction_date) AS tx_date,
        CAST(transaction_amount AS REAL) AS amount,
        TRIM(region) AS region
    FROM transactions
    WHERE LOWER(TRIM(transaction_status)) = 'completed'
),

-- Block 2: Pre-aggregate auxiliary table to 1 row per join key
cte_aux AS (
    SELECT 
        DATE(rate_date) AS rate_date,
        AVG(CAST(spot_rate AS REAL)) AS avg_rate
    FROM fx_rates
    GROUP BY DATE(rate_date)
),

-- Block 3: Join & apply row-level math / window functions
cte_joined AS (
    SELECT 
        f.customer_id,
        f.region,
        f.amount * COALESCE(a.avg_rate, 1.0) AS amount_usd,
        ROW_NUMBER() OVER (PARTITION BY f.region ORDER BY f.amount DESC) AS region_rank
    FROM cte_fact f
    LEFT JOIN cte_aux a ON f.tx_date = a.rate_date
)

-- Block 4: Target grain aggregation & presentation
SELECT 
    region,
    ROUND(SUM(amount_usd), 2) AS total_volume_usd,
    COUNT(DISTINCT customer_id) AS active_customers
FROM cte_joined
GROUP BY region
ORDER BY total_volume_usd DESC
LIMIT 5;
```

---

## Step 4: Defensive SQL & Sanity Verification

1. **Zero-Division Defense:** Wrap denominators with `NULLIF(col, 0)`.
2. **Missing Value Defense:** Wrap nullable join fields with `COALESCE(col, fallback)`.
3. **Grain Uniqueness Check:** Verify that `COUNT(*) = COUNT(DISTINCT grain_key)` in the output.

---

## SQL Execution Order vs Writing Order

| Execution Step | SQL Clause | What Happens |
| :--- | :--- | :--- |
| **1st** | `FROM` / `JOIN` | Tables are identified and joined |
| **2nd** | `WHERE` | Rows are filtered out early |
| **3rd** | `GROUP BY` | Rows are grouped into buckets (changing the grain) |
| **4th** | `HAVING` | Filter aggregate metrics |
| **5th** | `SELECT` / Window `OVER` | Columns, expressions, and window functions are evaluated |
| **6th** | `ORDER BY` | Rows are sorted |
| **7th** | `LIMIT` / `OFFSET` | Output row count is truncated |
