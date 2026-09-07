# 🧠 The Universal Pandas Problem-Solving Framework

> A battle-tested mental model and execution blueprint for solving business cases and technical interview questions using **Pandas**.

---

## 📑 Table of Contents
1. [The 4-Step Reverse Engineering Blueprint](#1-the-4-step-reverse-engineering-blueprint)
2. [Step 1: Target Output Deliverable (Start with the End in Mind)](#step-1-target-output-deliverable-start-with-the-end-in-mind)
3. [Step 2: Raw Data Audit & Gap Analysis](#step-2-raw-data-audit--gap-analysis)
4. [Step 3: Backward Code Transformation Pipeline](#step-3-backward-code-transformation-pipeline)
   - [Blueprint 1: Segment Aggregations & Metrics](#blueprint-1-segment-aggregations--metrics)
   - [Blueprint 2: Relational Joins & Safe Anti-Joins](#blueprint-2-relational-joins--safe-anti-joins)
   - [Blueprint 3: Time-Series & Windowing (Rolling & Growth)](#blueprint-3-time-series--windowing-rolling--growth)
   - [Blueprint 4: Reshaping (Pivot, Unstack, Melt)](#blueprint-4-reshaping-pivot-unstack-melt)
   - [Blueprint 5: Top-N & Ranking per Group](#blueprint-5-top-n--ranking-per-group)
5. [Step 4: Sanity Audit & Verification Assertions](#step-4-sanity-audit--verification-assertions)
6. [Business Request to Pandas Translation Cheat Sheet](#business-request-to-pandas-translation-cheat-sheet)

---

## 1. The 4-Step Reverse Engineering Blueprint

Always work backwards from what the stakeholder wants to see:

<pre style="background: transparent !important; background-color: transparent !important; border: none !important; font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.25; color: inherit; padding: 0; margin: 15px 0;">
┌────────────────────────────────────────────────────────┐
│ STEP 1: TARGET OUTPUT (The Destination)                │
│ • Identify Metric Formulas: Prompt Words ➔ Math Equation│
│ • Target Schema: Required columns & dimensions         │
│ • Target Grain: What does exactly 1 row represent?     │
│ • Target Visual Layout: Wide matrix vs Long table      │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 2: RAW DATA AUDIT (The Starting Point)            │
│ • Which datasets contain the raw fields?               │
│ • Identify quirks: Nulls, string types, join keys      │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 3: BACKWARD TRANSFORMATION PIPELINE (The Bridge)  │
│ • Ingest & Cast ➔ Filter Early ➔ Merge ➔ Group/Agg ➔   │
│   Derive Ratios ➔ Reshape                              │
│ • Vectorized and clean method-chaining                 │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 4: SANITY AUDIT & VERIFICATION (The Guarantee)    │
│ • Assert unique rows, valid metric bounds (0-100%)     │
│ • Guard against 0-division and join duplicates         │
└────────────────────────────────────────────────────────┘
</pre>

---

## Step 1: Target Output Deliverable (Start with the End in Mind)

Before writing any code or loading files, write down the **target contract**:

### 1. Target Schema & Metric Formulas (Deconstructing Stakeholder Requests)
What columns and calculated metrics must exist in the final dataframe? Translate stakeholder words into exact mathematical equations before touching code:
- **Forex Spread Margin Revenue:**
  - `Spread = Ask Rate - Bid Rate`
  - `Spread Margin % = (Ask Rate - Bid Rate) / Spot Rate`
  - `FX Revenue USD = Transaction Amount * Spread Margin %`
- **Dispute / Chargeback Loss Ratio:**
  - `Dispute Loss Ratio % = (Disputed Amount / Total Transaction Amount) * 100`
- **Return / Breach Rates (NACHA/Compliance):**
  - `Return Rate % = (Returned Transactions Count / Total Settled Count) * 100`
- **Time-Series Day-over-Day Growth:**
  - `DoD Growth % = (Today Volume - Yesterday Volume) / Yesterday Volume * 100`

### 2. Target Grain (Level of Detail)
What does **ONE ROW** in the final output represent?
- **Per Customer:** 1 row = 1 unique customer (`groupby('customer_id')`)
- **Per Region & Card Type:** 1 row = 1 region-card combination (`groupby(['region', 'card_type'])`)
- **Per Day:** 1 row = 1 calendar date (`pd.Grouper(freq='D')`)

### 3. Target Layout (Shape)
- **Tabular / Flat:** Standard rows and columns.
- **Wide Matrix:** Dimensions on rows and columns (e.g. `pivot` / `unstack`).
- **Normalized / Long:** Tidy `[id_vars, metric_name, metric_value]` for BI ingestion (e.g. `melt`).

---

## Step 2: Raw Data Audit & Gap Analysis

Inspect your inputs and identify what transformations are required to reach the Target Output:

1. **Source Mapping:**  
   - Where does each target column come from? Are all columns in one table or split across multiple tables (requiring merges)?
2. **Data Cleanliness & Types:**  
   - Are date columns stored as text? $\rightarrow$ Convert with `pd.to_datetime()`.
   - Are there trailing spaces in category strings? $\rightarrow$ Clean with `.str.strip()`.
   - Are there missing values or NaNs in filter keys? $\rightarrow$ Handle with `.fillna()`.
3. **Join Relationships:**  
   - If merging `customers` (1) with `transactions` (Many), ensure dimension keys are unique to prevent duplicate row explosion.

---

## Step 3: Backward Code Transformation Pipeline

Follow the standard execution sequence to build the output cleanly:

```
1. Ingest & Cast ➔ 2. Filter Early ➔ 3. Merge ➔ 4. Group/Aggregate ➔ 5. Derive Ratios ➔ 6. Reshape
```

### Blueprint 1: Segment Aggregations & Metrics
```python
summary_report = (
    raw_transactions
    # 1. Filter
    .query("status == 'APPROVED'")
    # 2. Group & Aggregate to the target grain
    .groupby(['region', 'card_type'], as_index=False)
    .agg(
        total_volume=('amount', 'sum'),
        total_tx=('transaction_id', 'count'),
        fraud_tx=('is_fraud', 'sum')
    )
    # 3. Derive required KPIs
    .assign(
        fraud_rate_pct=lambda d: (d['fraud_tx'] / d['total_tx'] * 100).fillna(0.0),
        avg_ticket=lambda d: (d['total_volume'] / d['total_tx']).fillna(0.0)
    )
    .sort_values(by='total_volume', ascending=False)
    .reset_index(drop=True)
)
```

---

### Blueprint 2: Relational Joins & Safe Anti-Joins
```python
# Anti-Join: Find onboarded customers who NEVER transacted
dormant_customers = (
    customers
    .merge(raw_transactions[['customer_id', 'transaction_id']], on='customer_id', how='left')
    .loc[lambda d: d['transaction_id'].isna()]
    .groupby('account_tier', as_index=False)
    .agg(
        dormant_user_count=('customer_id', 'nunique'),
        total_idle_balance=('account_balance', 'sum')
    )
    .sort_values(by='total_idle_balance', ascending=False)
    .reset_index(drop=True)
)
```

---

### Blueprint 3: Time-Series & Windowing (Rolling & Growth)
```python
daily_metrics = (
    raw_transactions
    .assign(tx_date=lambda d: pd.to_datetime(d['created_at']))
    .sort_values('tx_date')  # Sort first before rolling/shifting!
    .groupby(pd.Grouper(key='tx_date', freq='D'))
    .agg(daily_volume=('amount', 'sum'))
    .reset_index()
    .assign(
        rolling_7d_avg=lambda d: d['daily_volume'].rolling(window=7, min_periods=1).mean(),
        dod_growth_pct=lambda d: (d['daily_volume'].pct_change() * 100).fillna(0.0),
        cumulative_volume=lambda d: d['daily_volume'].cumsum()
    )
)
```

---

### Blueprint 4: Reshaping (Pivot, Unstack, Melt)
```python
# --- Long to Wide Matrix ---
wide_matrix = summary_report.pivot(
    index='region', 
    columns='card_type', 
    values='fraud_rate_pct'
).fillna(0.0)

# --- Wide to Long / Tidy BI Feed ---
melted_df = pd.melt(
    summary_report,
    id_vars=['region', 'card_type'],
    value_vars=['total_volume', 'total_tx', 'fraud_rate_pct'],
    var_name='metric_name',
    value_name='metric_value'
)
```

---

### Blueprint 5: Top-N & Ranking per Group
```python
top_3_merchants = (
    merchants
    .assign(
        rank_in_cat=lambda d: d.groupby('category')['monthly_volume'].rank(method='dense', ascending=False)
    )
    .query("rank_in_cat <= 3")
    .sort_values(['category', 'rank_in_cat'])
    .reset_index(drop=True)
)
```

---

### ⚡ Alternative Approach: Fast 2-Block Interview Method Chain

In live 20-30 minute coding interviews, you can also solve Step 3 by collapsing the 6 substeps into **2 high-speed blocks**:

<pre style="background: transparent !important; background-color: transparent !important; border: none !important; font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.25; color: inherit; padding: 0; margin: 15px 0;">
┌────────────────────────────────────────────────────────┐
│ 📦 BLOCK 1: INGEST & FILTER (Substeps 3.1 + 3.2)       │
│ Load and filter records in 1–2 lines using .query()    │
├────────────────────────────────────────────────────────┤
│ ⛓️ BLOCK 2: PIPELINE CHAIN (Substeps 3.3 to 3.6)       │
│ Merge ➔ Group/Aggregate ➔ Derive/Round ➔ Sort in ONE   │
│ continuous method chain                                │
└────────────────────────────────────────────────────────┘
</pre>

```python
# BLOCK 1: Ingest & filter early (Substeps 3.1 + 3.2)
tx = pd.read_csv('data/raw_transactions.csv').query("status == 'APPROVED'")
cust = pd.read_csv('data/customers.csv')

# BLOCK 2: Pipeline chain: Merge -> Group -> Derive -> Round -> Sort (Substeps 3.3 to 3.6)
fast_summary = (
    tx.merge(cust, on='customer_id', how='inner')
    .groupby('account_tier', as_index=False)
    .agg(
        total_customers=('customer_id', 'nunique'),
        total_volume=('amount', 'sum'),
        fraud_tx=('is_fraud', 'sum')
    )
    .assign(fraud_rate_pct=lambda d: (d['fraud_tx'] / d['total_customers'] * 100).round(2))
    .sort_values(by='total_volume', ascending=False)
    .reset_index(drop=True)
)
```

#### 🎯 Can this be used for all types & levels of questions?
**Yes, 100%.** Here is how the exact same 2-block structure handles every level from Junior to Principal:

| Difficulty Level | How the 2-Block Combination Works |
| :--- | :--- |
| 🟢 **Junior / Entry Level**<br>*(Single table aggregations)* | **Block 1:** Load single CSV.<br>**Block 2:** `.groupby().agg().sort_values()` *(Takes 60 seconds to write)*. |
| 🟡 **Mid-Level**<br>*(2-Table Merges, Anti-Joins, Ratios)* | **Block 1:** Load 2 CSVs with `.query()` filters.<br>**Block 2:** `.merge().groupby().agg().assign(ratio=...).sort_values()` *(Takes 3 mins)*. |
| 🔴 **Senior / Staff Level**<br>*(Multi-Format JSON/TSV, Window Functions)* | **Block 1:** Load JSON / TSV with `json_normalize()`.<br>**Block 2:** Pre-aggregate child table ➔ `.merge()` ➔ `.groupby()` ➔ `.rolling()` ➔ `.sort_values()` *(Takes 5 mins)*. |

#### 🎯 Why interviewers love this pattern:
* **Zero Temporary Clutter:** It doesn't pollute the notebook with 5 unnecessary temporary DataFrames (`df1`, `df2`, `df_temp`).
* **SQL-Like Readability:** Senior engineers read it naturally like a SQL query (`SELECT` ➔ `FROM` ➔ `WHERE` ➔ `GROUP BY` ➔ `ORDER BY`).
* **Speed:** It cuts your coding time in half, giving you extra minutes for assertions and discussion.

---

## Step 4: Sanity Audit & Verification Assertions

Before submitting your solution, run a quick automated sanity check:

```python
# ==========================================
# 🛡️ DEFENSIVE SANITY AUDIT
# ==========================================
# 1. Verify Target Grain (No duplicate keys in output)
assert not summary_report.duplicated(subset=['region', 'card_type']).any(), "Duplicate grain found!"

# 2. Verify Valid Metric Bounds (e.g. percentages between 0 and 100)
assert summary_report['fraud_rate_pct'].between(0, 100).all(), "Fraud rate exceeds valid bounds!"

# 3. Verify No Unexpected NaNs
assert summary_report[['total_volume', 'total_tx']].isna().sum().sum() == 0, "Unexpected nulls in core metrics!"

print("✅ All validation checks passed successfully!")
```

---

## Business Request to Pandas Translation Cheat Sheet

| Stakeholder / Business Requirement | Pandas Mechanism |
| :--- | :--- |
| *"Only include active / completed / non-fraud records"* | `df.query("status == 'COMPLETED'")` |
| *"Match customers with their transactions"* | `df.merge(customers, on='customer_id', how='left')` |
| *"Users who NEVER did action X"* | Left join + `.loc[lambda d: d['action_id'].isna()]` |
| *"Total / Average / Min / Max per segment"* | `.groupby([...]).agg(col_name=('source_col', 'func'))` |
| *"Top N per group with ties allowed"* | `.groupby('group')['col'].rank(method='dense')` |
| *"Day-over-day growth / 7-day rolling"* | `.pct_change() * 100` / `.rolling(7, min_periods=1).mean()` |
| *"Create side-by-side executive grid"* | `df.pivot(index=..., columns=..., values=...)` |
| *"Unpivot metrics into rows for BI tools"* | `pd.melt(df, id_vars=[...], value_vars=[...])` |
