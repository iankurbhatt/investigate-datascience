# 🧠 The Universal NumPy Problem-Solving Framework

> A battle-tested mental model and execution blueprint for solving high-performance numerical algorithms, quantitative finance models, and technical interview cases using **NumPy**.

---

## 📑 Table of Contents
1. [The 5-Step Universal Problem-Solving Blueprint](#1-the-5-step-universal-problem-solving-blueprint)
2. [Step 0: Scenario Decoding & Raw Matrix Reconnaissance (The Groundwork)](#step-0-scenario-decoding--raw-matrix-reconnaissance-the-groundwork)
3. [Step 1: Target Output Contract (Start with the End in Mind)](#step-1-target-output-contract-start-with-the-end-in-mind)
4. [Step 2: Raw Array Audit & Memory Gap Analysis](#step-2-raw-array-audit--memory-gap-analysis)
5. [Step 3: Backward Code Transformation Pipeline](#step-3-backward-code-transformation-pipeline)
   - [Blueprint 1: Vectorized Arithmetic & Ufuncs](#blueprint-1-vectorized-arithmetic--ufuncs)
   - [Blueprint 2: Axis Aggregations & Directional Reductions](#blueprint-2-axis-aggregations--directional-reductions)
   - [Blueprint 3: Broadcasting & Multi-Dimensional Alignment](#blueprint-3-broadcasting--multi-dimensional-alignment)
   - [Blueprint 4: Zero-Copy Sliding Windows & Convolution](#blueprint-4-zero-copy-sliding-windows--convolution)
   - [Blueprint 5: Linear Algebra & Matrix Solvers](#blueprint-5-linear-algebra--matrix-solvers)
   - [Blueprint 6: Fast Top-K, Ranking & Binary Search](#blueprint-6-fast-top-k-ranking--binary-search)
6. [Step 4: Sanity Audit & Numerical Assertions](#step-4-sanity-audit--numerical-assertions)
7. [Business & Math Translation to NumPy Rosetta Stone](#business--math-translation-to-numpy-rosetta-stone)

---

## 1. The 5-Step Universal Problem-Solving Blueprint

Always start with thorough scenario comprehension and groundwork, then work backwards from the numerical contract:

<pre style="background: transparent !important; background-color: transparent !important; border: none !important; font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.25; color: inherit; padding: 0; margin: 15px 0;">
┌────────────────────────────────────────────────────────┐
│ STEP 0: SCENARIO DECODING & RECONNAISSANCE (Groundwork)│
│ • Read the problem statement 10 times thoroughly       │
│ • Identify mathematical formulas & physical boundaries │
│ • Inspect raw array shapes, dimensions & dtypes       │
│ • (Revisit & re-verify after defining Step 1 contract) │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 1: TARGET OUTPUT CONTRACT (The Destination)       │
│ • Target Tensor Shape: 1D (N,), 2D (N, M), Scalar?     │
│ • Target Data Type: float64, float32, int32, bool?     │
│ • Target Metric Equation: Math equation & units        │
│ • Target Grain: What does 1 index/row represent?       │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 2: RAW ARRAY AUDIT & MEMORY GAPS (Starting Point) │
│ • Inspect .shape, .dtype, .strides, .flags.c_contiguous│
│ • Audit edge cases: NaNs, Infs, zeros (divide-by-zero) │
│ • Memory budget: Will this cause an OOM deep copy?     │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 3: BACKWARD TRANSFORMATION PIPELINE (The Bridge)  │
│ • Cast / Clean ➔ Align Dimensions ➔ Vectorize Ufuncs ➔ │
│   Aggregate across Axes ➔ Solve / Transform            │
│ • Enforce self-documenting variable names & 0-loops    │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ STEP 4: SANITY AUDIT & NUMERICAL ASSERTIONS (Guarantee)│
│ • Assert exact output shapes: assert res.shape == (N,) │
│ • Assert bounds & finiteness: np.all(np.isfinite(res)) │
│ • Assert precision tolerance: np.allclose(a, b, 1e-7)  │
└────────────────────────────────────────────────────────┘
</pre>

---

## Step 0: Scenario Decoding & Raw Matrix Reconnaissance (The Groundwork)

> **Core Idea:** 90% of numerical bugs happen because engineers start writing loops or matrix multiplications without verifying dimensions, units, or edge-case zeros.

### 🔹 1. Read the Scenario 10 Times
- Do **not** touch code or write `np.array` immediately.
- Read through the stakeholder / mathematical brief at least **10 times** until the physical simulation, financial payoff, or risk model is completely clear.

### 🔹 2. Break Words & Lines into Mathematical Rules
- Translate stakeholder terms into explicit mathematical invariants:
  - *“Mean-centered normalized return”* $\rightarrow Z = \frac{X - \mu}{\sigma}$
  - *“Rolling 30-day volatility”* $\rightarrow \text{std}(\text{sliding\_window}(X, 30))$
  - *“Portfolio variance”* $\rightarrow \sigma_p^2 = w^T \Sigma w$

### 🔹 3. Inspect Raw Matrix Dimensions & Dtypes
- What are the incoming tensor shapes? (e.g. `(N, D)` feature matrix, `(D,)` weight vector).
- Are dimensions aligned for inner products $(N, D) \times (D, 1) \rightarrow (N, 1)$?
- Are there missing numbers (`NaN`), infinite asymptotes (`Inf`), or zeros in denominators?

---

## Step 1: Target Output Contract (Start with the End in Mind)

Before allocating any memory or writing functions, write down the **target contract**:

### 1. Target Schema, Shape & Equation
| Property | Target Contract Specification |
| :--- | :--- |
| **Output Shape** | e.g. `(N, 1)` column vector or `(N, K)` probability matrix |
| **Data Type (`dtype`)** | `np.float64` (double precision) or `np.float32` (GPU/DL standard) |
| **Mathematical Equation** | $\hat{y} = \sigma(X W + b)$ |
| **Physical Units / Range** | Values must strictly reside in $[0.0, 1.0]$ |

```python
# Target Contract Definition Example
target_shape = (num_customers, 1)
target_dtype = np.float64
# Invariant: All probabilities must sum to 1.0 across axis=1
```

---

## Step 2: Raw Array Audit & Memory Gap Analysis

Inspect the raw input memory layout to prevent bottlenecks and unintended copies:

```python
# Inspect array foundations
print("Input Shape   :", raw_features.shape)
print("Data Type     :", raw_features.dtype)
print("Byte Strides  :", raw_features.strides)
print("Contiguity    :", raw_features.flags.c_contiguous)
print("NaN Count     :", np.isnan(raw_features).sum())
print("Inf Count     :", np.isinf(raw_features).sum())
```

### ⚠️ Common Numerical Gotchas:
1. **Integer Division Truncation:** `np.array([1, 2]) / 2` vs `//` floor division.
2. **Dimension Mismatch in Broadcasting:** Adding `(4, 3)` to `(4,)` throws `ValueError`. Must align to `(4, 1)`!
3. **Implicit Deep Copies vs Views:** Slices `arr[0:5]` are views; fancy indexing `arr[[0, 1, 2]]` creates a deep copy.
4. **NaN Contamination:** A single `NaN` causes `np.sum()` to return `NaN`. Use `np.nansum()`.

---

## Step 3: Backward Code Transformation Pipeline

Select the appropriate **Battle-Tested Blueprint** for the computation:

### Blueprint 1: Vectorized Arithmetic & Ufuncs
*Used for element-wise transformations, financial returns, and activation functions.*

```python
# Self-documenting, loop-free vectorized computation
daily_asset_returns = np.array([0.012, -0.005, 0.034, -0.018])
log_asset_returns = np.log1p(daily_asset_returns)  # Numerically stable log(1 + x)
high_water_mark_peak = np.maximum.accumulate(log_asset_returns)
```

---

### Blueprint 2: Axis Aggregations & Directional Reductions
*Used for feature summarization, per-user totals, and cross-sectional rankings.*

```python
# Rule of Axis: axis=0 collapses ROWS (column stats), axis=1 collapses COLUMNS (row stats)
user_transaction_matrix = np.array([
    [100.0, 250.0, 300.0],
    [400.0, 150.0, 600.0]
])

# preserve dimensions with keepdims=True to enable direct broadcasting!
user_average_spend = user_transaction_matrix.mean(axis=1, keepdims=True)  # Shape (2, 1)
mean_centered_spend = user_transaction_matrix - user_average_spend        # Shape (2, 3)
```

---

### Blueprint 3: Broadcasting & Multi-Dimensional Alignment
*Used for feature normalization, distance matrices, and outer payoff grids.*

```python
# Aligning column vector (N, 1) with row vector (1, M) to create (N, M) grid
interest_rate_schedule = np.array([0.03, 0.05, 0.07])[:, None]  # Shape (3, 1)
loan_principal_amounts = np.array([10000, 50000, 100000])        # Shape (3,)

# Virtual stretching with zero RAM overhead
annual_interest_grid = interest_rate_schedule * loan_principal_amounts  # Shape (3, 3)
```

---

### Blueprint 4: Zero-Copy Sliding Windows & Convolution
*Used for rolling volatility, Bollinger Bands, and signal filtering without loops.*

```python
from numpy.lib.stride_tricks import sliding_window_view

stock_price_stream = np.array([100.0, 102.0, 105.0, 101.0, 108.0, 115.0])

# Creates rolling 3-day windows with 0 extra memory allocation
rolling_price_windows = sliding_window_view(stock_price_stream, window_shape=3)
rolling_3day_moving_avg = rolling_price_windows.mean(axis=1)
rolling_3day_volatility = rolling_price_windows.std(axis=1)
```

---

### Blueprint 5: Linear Algebra & Matrix Solvers
*Used for portfolio optimization, solving linear systems $Ax = b$, and PCA.*

```python
# Solving systems of linear equations directly in O(N^3)
# 2x + 3y = 8
# 4x + 9y = 20
coefficient_matrix_A = np.array([[2.0, 3.0], [4.0, 9.0]])
target_vector_b = np.array([8.0, 20.0])

solved_parameters_x = np.linalg.solve(coefficient_matrix_A, target_vector_b)
```

---

### Blueprint 6: Fast Top-K, Ranking & Binary Search
*Used for $O(N)$ partial sorting, index ranking, and $O(\log N)$ quantile binning.*

```python
# 1. Top-K Selection in O(N) time without full sort
api_latencies_ms = np.array([12, 45, 98, 23, 150, 87, 34, 210, 56])
worst_3_indices = np.argpartition(api_latencies_ms, -3)[-3:]
worst_3_latencies = api_latencies_ms[worst_3_indices]

# 2. O(log N) Binary Search Bucket Assignment
score_bins = np.array([580, 670, 740, 800])
customer_ficos = np.array([620, 710, 850, 550, 780])
assigned_tier_ids = np.searchsorted(score_bins, customer_ficos)
```

---

## Step 4: Sanity Audit & Numerical Assertions

Never deliver numerical output without automated defensive assertions:

```python
def verify_numerical_deliverable(result_array, expected_shape, min_bound=None, max_bound=None):
    # 1. Shape Assertion
    assert result_array.shape == expected_shape, f"Shape mismatch: {result_array.shape} vs {expected_shape}"
    
    # 2. Finite Number Assertion (No NaNs or Infs)
    assert np.all(np.isfinite(result_array)), "Numerical error: Output contains NaN or Inf!"
    
    # 3. Value Boundary Assertions
    if min_bound is not None:
        assert np.all(result_array >= min_bound), f"Boundary error: Values found below {min_bound}"
    if max_bound is not None:
        assert np.all(result_array <= max_bound), f"Boundary error: Values found above {max_bound}"
        
    print("✅ All Numerical Sanity Assertions Passed!")
```

---

## Business & Math Translation to NumPy Rosetta Stone

| Business / Math Requirement | NumPy Method | Equivalent Pandas | Equivalent SQL |
| :--- | :--- | :--- | :--- |
| **Row-wise / Column-wise Mean** | `arr.mean(axis=0)` / `axis=1` | `df.mean(axis=0)` / `axis=1` | `AVG(val) GROUP BY col` |
| **Conditional If-Else / Flag** | `np.where(arr > 0, 1, 0)` | `np.where(...)` / `.map()` | `CASE WHEN val > 0 THEN 1 ELSE 0 END` |
| **Rolling Moving Average** | `sliding_window_view(arr, 3).mean(1)` | `df['col'].rolling(3).mean()` | `AVG(val) OVER (ROWS 2 PRECEDING)` |
| **Top-K Worst Latencies** | `np.argpartition(arr, -K)[-K:]` | `df.nlargest(K, 'col')` | `ORDER BY val DESC LIMIT K` |
| **Bucket / Tier Binning** | `np.searchsorted(bins, vals)` | `pd.cut(vals, bins)` | `CASE WHEN val < 580 THEN 'Tier 1'...` |
| **Unique Values & Counts** | `np.unique(arr, return_counts=True)` | `df['col'].value_counts()` | `SELECT col, COUNT(*) GROUP BY col` |
| **Vector Dot Product** | `weights @ features` | `df.dot(weights)` | `SUM(weight * feature)` |
| **Clamping / Outlier Winsorization**| `np.clip(arr, min_val, max_val)` | `df['col'].clip(lower, upper)` | `LEAST(GREATEST(val, min), max)` |
| **Membership Blacklist Filter** | `np.isin(arr, blacklist)` | `df['col'].isin(blacklist)` | `WHERE col IN (SELECT ...)` |
