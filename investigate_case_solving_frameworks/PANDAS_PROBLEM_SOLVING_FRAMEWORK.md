# 🧠 The Universal Pandas Problem-Solving Framework

> A battle-tested mental model and execution blueprint for solving business cases and technical interview questions using **Pandas**.

---

## 📑 Table of Contents
1. [The 5-Step Universal Problem-Solving Blueprint](#1-the-5-step-universal-problem-solving-blueprint)
2. [Step 0: Scenario Decoding & Raw Schema Reconnaissance (The Groundwork)](#step-0-scenario-decoding--raw-schema-reconnaissance-the-groundwork)
3. [Step 1: Target Output Deliverable (Start with the End in Mind)](#step-1-target-output-deliverable-start-with-the-end-in-mind)
4. [Step 2: Raw Data Audit & Gap Analysis](#step-2-raw-data-audit--gap-analysis)
5. [Step 3: Backward Code Transformation Pipeline](#step-3-backward-code-transformation-pipeline)
   - [Blueprint 1: Segment Aggregations & Metrics](#blueprint-1-segment-aggregations--metrics)
   - [Blueprint 2: Relational Joins & Safe Anti-Joins](#blueprint-2-relational-joins--safe-anti-joins)
   - [Blueprint 3: Time-Series & Windowing (Rolling & Growth)](#blueprint-3-time-series--windowing-rolling--growth)
   - [Blueprint 4: Reshaping (Pivot, Unstack, Melt)](#blueprint-4-reshaping-pivot-unstack-melt)
   - [Blueprint 5: Top-N & Ranking per Group](#blueprint-5-top-n--ranking-per-group)
6. [Step 4: Sanity Audit & Verification Assertions](#step-4-sanity-audit--verification-assertions)
7. [Business Request to Pandas Translation Cheat Sheet](#business-request-to-pandas-translation-cheat-sheet)

---

## 1. The 5-Step Universal Problem-Solving Blueprint

Always start with thorough scenario comprehension and groundwork, then work backwards from the stakeholder deliverable:

<pre style="background: transparent !important; background-color: transparent !important; border: none !important; font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.25; color: inherit; padding: 0; margin: 15px 0;">
┌────────────────────────────────────────────────────────┐
│ STEP 0: SCENARIO DECODING & RECONNAISSANCE (Groundwork)│
│ • Read the case scenario 10 times thoroughly          │
│ • Break words & sentences into discrete business rules │
│ • Extract & inspect all tables: rows, cols, data types │
│ • (Revisit & re-verify after defining Step 1 contract) │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 1: TARGET OUTPUT CONTRACT (The Destination)       │
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

## Step 0: Scenario Decoding & Raw Schema Reconnaissance (The Groundwork)

> **Core Idea:** 90% of interview mistakes happen because candidates rush into code without truly understanding the business scenario or the raw data schemas.

### 🔹 1. Read the Case Scenario 10 Times
- Do **not** touch code or write imports immediately.
- Read through the stakeholder brief at least **10 times** until the end-to-end business narrative (fraud attack, liquidity squeeze, AML structuring, underwriting cohort) is crystal clear in your mind.

### 🔹 2. Break the Words & Lines of the Scenario Paragraphs
- Dissect the prompt sentence by sentence, phrase by phrase:
  - *What constitutes an active session?*
  - *Which specific filters or status flags apply?*
  - *What business conditions trigger a risk flag?*
- Decode complex stakeholder terminology into plain computational logic.

### 🔹 3. Extract & Inspect Every Table Schema
- Identify all tables involved in the scenario.
- Perform an initial schema reconnaissance:
  - Inspect sample rows (`head(3)` or `LIMIT 3`).
  - Count columns and rows.
  - Verify data types: timestamps (ISO strings?), numeric amounts (floats or strings?), booleans (ints `0/1` or strings `'True'/'False'`), categorical keys (extra whitespace?).

### 🔹 4. Move to Step 1 & Revisit to Re-Verify
- Once you define the **Step 1: Target Output Contract**, **revisit Step 0** to double-check that every nuance, metric, and edge case from the prompt is accurately captured in your Target Contract.

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

## Step 3: Backward Code Transformation Pipeline (The 9-Step Master Architecture)

1. Ingest & Flatten ➔ 2. Clean & Cast ➔ 3. Filter Early ➔ 4. Pre-Aggregate ➔ 5. Relational Merge ➔ 6. Window & Bin ➔ 7. Group & Aggregate ➔ 8. Derive & Transition ➔ 9. Reshape, Rank & Sort

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. INGEST & FLATTEN      : Multi-format parsing (JSONL/XML/DAT/YAML), .explode()       │
│ 2. CLEAN & CAST          : Strip whitespace, title-case, coerce numerics, parse dates │
│ 3. FILTER EARLY          : Discard out-of-scope records early to maximize speed        │
│ 4. PRE-AGGREGATE         : Collapse 1-to-Many child tables to 1:1 grain before merge   │
│ 5. RELATIONAL MERGE      : Safe 1-to-1 joins / Anti-joins with validate='1:1'          │
│ 6. WINDOW & BINNING      : .rolling(), .ewm(), .shift(), pd.cut(), np.select()        │
│ 7. GROUP & AGGREGATE     : Group by dimensions to reach exact target grain             │
│ 8. DERIVE & TRANSITION   : Calculate KPIs, loss rates, or Markov pd.crosstab() matrices│
│ 9. RESHAPE, RANK & SORT  : .pivot(), .rank(), .sort_values(), .round(2)               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 📖 Complete Methods Directory (All Operations by Step):

| Step # | Pipeline Stage | Primary Focus | Exact Methods & Functions Used |
| :---: | :--- | :--- | :--- |
| **1** | **Ingest & Flatten** | Multi-Format Parsing & Unnesting | `pd.read_csv()`, `pd.read_json(lines=True)`, `pd.json_normalize()`, `ET.parse()`, `pd.read_fwf()`, `yaml.safe_load()`, `.explode()`, `pd.DataFrame.from_dict()` |
| **2** | **Clean & Cast** | Type Coercion & Normalization | `pd.to_datetime()`, `pd.to_numeric(errors='coerce')`, `.astype()`, `.str.strip()`, `.str.title()`, `.str.upper()`, `.str.replace()`, `.fillna()`, `.dropna()`, `.clip()` |
| **3** | **Filter Early** | Fast Row Reduction | `.query()`, `.loc[]`, `.isin()`, `.between()`, `.str.contains()`, `.str.startswith()`, `~` (Bitwise NOT), `&` / `\|` |
| **4** | **Pre-Aggregate** | Grain Alignment (1:1 before Merge) | `.groupby(as_index=False).agg()`, Named Aggregations (`total=('amount', 'sum')`), `.drop_duplicates(subset=[...])`, `.size()` |
| **5** | **Relational Merge** | Safe Joins & Anti-Joins | `.merge(how='inner'\|'left')`, `validate='1:1'`, `validate='m:1'`, `pd.merge_asof()`, Anti-Join Pattern (`indicator=True` + `.query("_merge == 'left_only'")`), `pd.concat()` |
| **6** | **Window & Binning** | Time-Series & Rule Engines | `.rolling(window=N)`, `.ewm(span=N)`, `.shift(N)`, `.pct_change()`, `.cumsum()`, `pd.Grouper(freq='D')`, `pd.cut()`, `pd.qcut()`, `np.select()`, `np.where()`, Island-and-Gap `(cond != cond.shift()).cumsum()` |
| **7** | **Group & Aggregate** | Target Grain Summary | `.groupby(['dim1', 'dim2']).agg()`, `nunique`, `.transform()`, `.filter(lambda g: ...)` |
| **8** | **Derive & Transition**| KPI Ratios & Markov Probabilities | `.assign(lambda d: ...)`, `pd.crosstab(normalize='index')`, Defensive division `(a / b * 100).fillna(0.0)`, `.diff()` |
| **9** | **Reshape, Rank & Sort**| Final Layout & Presentation | `.pivot()`, `.melt()`, `.unstack()`, `.stack()`, `.rank(method='dense')`, `.nlargest()`, `.sort_values()`, `.round(2)`, `.reset_index(drop=True)` |

---

### 🧠 Mental Model: Methods Used at Multiple Stages (The Grain Boundary)

> **Why do methods like `.assign()`, `.query()`, `.sort_values()`, and `.fillna()` appear at both the beginning AND the end of a pipeline?**

Every Pandas pipeline crosses **one critical turning point**: the **`.groupby().agg()`** Grain Boundary.

```
                      ┌──────────────────────────────────────────────┐
                      │             WORLD 1: RAW ROWS                │
                      │  (Individual transactions, events, users)   │
                      └──────────────────────┬───────────────────────┘
                                             ▼
                                ⚡ THE GROUPBY CHECKPOINT ⚡
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │            WORLD 2: SUMMARY ROWS             │
                      │       (Aggregated segments & totals)         │
                      └──────────────────────────────────────────────┘
```

| Method | Role in World 1 (BEFORE GroupBy) | Role in World 2 (AFTER GroupBy) |
| :--- | :--- | :--- |
| **`.assign()`** | **Data Cleaning:** Strip strings, parse dates, cast types.<br>*(e.g., `.assign(tx_date=pd.to_datetime(...))`)* | **KPI Ratios:** Calculate percentages and margins.<br>*(e.g., `.assign(fraud_rate_pct=fraud/total*100))`)* |
| **`.query()`** | **Data Hygiene:** Remove inactive accounts or test records.<br>*(e.g., `.query("status == 'APPROVED'")`)* | **Threshold Filter:** Filter summary groups by KPI.<br>*(e.g., `.query("total_volume > 1_000_000")`)* |
| **`.sort_values()`**| **Time-Series Alignment:** Sort by date *before* rolling/shift.<br>*(e.g., `.sort_values('tx_date')`)* | **Final Presentation:** Sort by highest risk or volume.<br>*(e.g., `.sort_values('total_exposed_usd', ascending=False)`)* |
| **`.fillna()`** | **Dirty Data Defense:** Replace missing raw balances with `0.0`.<br>*(e.g., `.fillna({'account_balance': 0.0})`)* | **Division Defense:** Replace `NaN` from 0-division with `0.0`.<br>*(e.g., `.assign(rate=...).fillna(0.0)`)* |
| **`.round()`** | **Raw Precision:** Round raw currency amounts.<br>*(e.g., `df['amount'].round(2)`)* | **Final Output Polish:** Round all final KPI percentages to 2 decimals.<br>*(e.g., `.round(2)` at the very bottom)* |

---

### ⚡ The Fast 2-Block Interview Blueprint
In live 20-30 minute coding interviews, collapse these 9 steps into **2 high-speed method blocks**:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ 📦 BLOCK 1: Data Preparation & Pre-Aggregation                                │
│    • Steps 1–4: Ingest, Clean, Filter, and Pre-Aggregate child tables to 1:1   │
├────────────────────────────────────────────────────────────────────────────────┤
│ ⛓️ BLOCK 2: Master Transformation Chain                                        │
│    • Steps 5–9: Merge ➔ Window/Bin ➔ Group/Agg ➔ Derive KPIs ➔ Rank & Sort     │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

### 📘 Master Blueprints by Category:

#### Blueprint 1: Multi-Format Ingest, Nested Flattening & Cleaning (Steps 1–2)
```python
import json, xml.etree.ElementTree as ET

# Nested JSON / JSONL flattening
telemetry = pd.read_json('data/device_telemetry.jsonl', lines=True)

# XML Parsing to DataFrame
tree = ET.parse('data/credit_bureau_scores.xml')
records = [{'customer_id': n.findtext('id'), 'fico': int(n.findtext('fico'))} for n in tree.findall('report')]
bureau = pd.DataFrame(records)
```

#### Blueprint 2: Pre-Aggregation (Granularity Alignment before Merge) (Steps 3–4)
```python
# Prevent 1-to-Many join row explosion by pre-aggregating child sub-table
flagged_bot_sessions = (
    telemetry
    .query("latency_ms <= 60 and (network_type == 'Tor-Proxy' or is_rooted_jailbroken == True)")
    .groupby('customer_id', as_index=False)
    .agg(avg_latency=('latency_ms', 'mean'), bot_session_count=('session_id', 'count'))
)
```

#### Blueprint 3: Relational Joins & Safe Anti-Joins (Step 5)
```python
# Safe 1:1 Merge
exposure_df = customers.merge(flagged_bot_sessions, on='customer_id', how='inner', validate='1:1')
```

#### Blueprint 4: Time-Series Windowing, EWMA & Island-and-Gap Streaks (Step 6)
```python
# Rolling 7D, EWMA 14D & Acceleration
fx_ts = (
    transactions
    .assign(tx_date=lambda d: pd.to_datetime(d['created_at']))
    .sort_values('tx_date')
    .groupby([pd.Grouper(key='tx_date', freq='D'), 'currency_pair'])
    .agg(daily_volume=('amount', 'sum'))
    .reset_index()
    .assign(
        rolling_7d_vol=lambda d: d.groupby('currency_pair')['daily_volume'].rolling(7, min_periods=1).mean().values,
        ewm_14d_vol=lambda d: d.groupby('currency_pair')['daily_volume'].ewm(span=14).mean().values,
        acceleration=lambda d: d['rolling_7d_vol'] - d['ewm_14d_vol']
    )
)

# Island-and-Gap Consecutive Streak Tracking
streak_df = (
    transactions
    .sort_values(['customer_id', 'tx_date'])
    .assign(
        is_breach=lambda d: d['status'] == 'FAILED',
        streak_id=lambda d: (d['is_breach'] != d.groupby('customer_id')['is_breach'].shift(1)).cumsum()
    )
)
```

#### Blueprint 5: Vectorized Continuous Binning & Underwriting Engine (Step 6)
```python
# FICO Banding & np.select underwriting rules
underwriting_df = (
    customers
    .assign(
        fico_band=lambda d: pd.cut(
            d['fico_score'], 
            bins=[300, 580, 670, 740, 800, 850], 
            labels=['Deep Subprime', 'Subprime', 'Near Prime', 'Prime', 'Super Prime']
        ),
        underwriting_decision=lambda d: np.select(
            condlist=[
                d['fico_score'] >= 740,
                (d['fico_score'] >= 650) & (d['annual_income'] >= 60000),
                d['fico_score'] < 580
            ],
            choicelist=['AUTO_APPROVE', 'MANUAL_REVIEW', 'AUTO_DECLINE'],
            default='MANUAL_REVIEW'
        )
    )
)
```

#### Blueprint 6: Group Aggregation, Markov Transitions & Cross-Tabs (Steps 7–8)
```python
# Cohort Credit Rating Markov Transition Matrix
transition_matrix = pd.crosstab(
    underwriting_df['origination_tier'],
    underwriting_df['current_tier'],
    normalize='index'  # Row probabilities sum to 100%
).round(4) * 100
```

#### Blueprint 7: Reshaping, Top-N Ranking & Sorting (Step 9)
```python
# Dense Window Ranking & Top-N Per Group
top_risk_ranked = (
    summary_report
    .assign(risk_rank=lambda d: d.groupby('region')['loss_amount'].rank(ascending=False, method='dense'))
    .query("risk_rank <= 3")
    .sort_values(by=['region', 'risk_rank'])
    .reset_index(drop=True)
)
```
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
