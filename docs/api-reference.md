# API reference

All public functions accept a pandas `DataFrame` with a single-level column
index, validate it, and leave it unchanged. Percentage parameters and output
percentages use the `0..100` scale; ratio parameters use `0..1` unless noted
otherwise. Numeric configuration rejects booleans, `NaN`, and infinity.

The supported public API is exported from `framepeek`. Implementation is
grouped into `analysis`, `validation`, `warnings`, and `report`; configuration
aliases `ColumnName`, `CorrelationMethod`, `OutlierMethod`, and `Severity` are
also public. Modules prefixed with `_`, including `_context`, are internal and
not part of the compatibility contract.

## Full report

### `profile`

```python
profile(
    df,
    target_column=None,
    correlation_method="pearson",
    outlier_method="iqr",
    outlier_multiplier=1.5,
    top_n_categories=5,
    missing_thresholds=(5, 20, 50),
    warning_missing_threshold=20,
    high_cardinality_ratio=0.5,
    imbalance_ratio=3,
)
```

| Parameter | Meaning |
| --- | --- |
| `df` | Non-empty pandas `DataFrame` with unique column names. |
| `target_column` | Optional existing column name to analyze as the target. |
| `correlation_method` | `pearson`, `spearman`, or `kendall`. |
| `outlier_method` | Outlier method; the MVP supports only `iqr`. |
| `outlier_multiplier` | Positive multiplier applied to the IQR bounds. |
| `top_n_categories` | Positive number of leading values retained per categorical column. |
| `missing_thresholds` | Three increasing severity boundaries within `0..100`. |
| `warning_missing_threshold` | Missing percentage above which a warning is emitted. |
| `high_cardinality_ratio` | Categorical unique-value ratio within `(0, 1]`. |
| `imbalance_ratio` | Majority-to-minority ratio above which a target is imbalanced; must exceed `1`. |

Returns a dictionary with exactly ten keys: `overview`, `columns`, `missing`,
`duplicates`, `numeric`, `categorical`, `outliers`, `correlations`, `target`,
and `warnings`.

### `print_report(report)`

Prints every top-level report section under a title. Nested tables receive
subheadings, and rows, columns, and long cell values are not replaced with
formatter-generated ellipses. It returns `None` without changing the report or
global pandas display options.

## Validation and dataset summaries

### `validate(df, target_column=None)`

Validates the shared input rules. Returns `None`. Raises `TypeError` for a
non-DataFrame or MultiIndex columns, `ValueError` for an empty DataFrame or
duplicate column names, and `KeyError` for an unknown target. Duplicate-column
errors include each repeated label and its occurrence count.

### `overview(df)`

Returns a two-column `DataFrame` (`metric`, `value`) containing dimensions,
missing and duplicate totals, memory use, and column-type counts.

### `columns(df, high_cardinality_ratio=0.5)`

Returns one `DataFrame` row per column with dtype, inferred type, completeness,
cardinality, leading value, and identifier/constant/high-cardinality flags.
`high_cardinality_ratio` must be within `(0, 1]`.

### `missing(df, thresholds=(5, 20, 50))`

Returns a `DataFrame` with `column`, `missing`, `missing_pct`, `non_missing`,
`severity`, and `rank`. Row-level totals are stored in
`result.attrs["rows"]`. `thresholds` must be a tuple of three increasing values
within `0..100`.

### `duplicates(df, subset=None, max_examples=5)`

Returns a dictionary with `duplicate_rows`, `duplicate_pct`,
`duplicate_groups`, `unique_rows`, `groups`, and `examples`. `subset` optionally
selects existing columns; `max_examples` is a non-negative integer.

## Column analyses

### `numeric(df)`

Returns one `DataFrame` row per numeric, non-boolean column. It includes count,
missingness, center, spread, quartiles, skewness, kurtosis, zero counts, and
negative-value counts. Returns an empty table with stable columns when there
are no numeric columns.

### `categorical(df, top_n=5, rare_max_count=1)`

Returns one `DataFrame` row per categorical or boolean column with cardinality,
the leading value, top values, and rare/singleton counts. `top_n` must be a
positive integer and `rare_max_count` must be at least one.

### `outliers(df, method="iqr", multiplier=1.5)`

Returns one `DataFrame` row per numeric, non-boolean column with IQR bounds and
potential outlier counts. `method` must be `iqr`; `multiplier` must be positive.
Results are diagnostic and do not remove values.

### `correlations(df, method="pearson", threshold=0)`

Returns `{"matrix": DataFrame, "pairs": DataFrame}` for numeric, non-boolean
columns. `method` accepts `pearson`, `spearman`, or `kendall`; `threshold`
filters pairs by absolute correlation and must be within `0..1`.

### `target(df, target_column, imbalance_ratio=3)`

Analyzes an existing target column. Targets with at most 20 non-missing unique
values, plus categorical and boolean targets, return a categorical dictionary
with distribution and imbalance fields. Other numeric targets return a
dictionary with numeric summary, outliers, and correlations.
`imbalance_ratio` must exceed one.

## Warnings

### `warnings`

```python
warnings(
    df,
    target_column=None,
    missing_threshold=20,
    near_constant_ratio=0.95,
    high_cardinality_ratio=0.5,
    outlier_threshold=5,
    imbalance_ratio=3,
)
```

Returns a `DataFrame` with `code`, `severity`, `column`, `message`,
`recommendation`, and `metric`.

| Code | Trigger |
| --- | --- |
| `duplicate_rows` | One or more duplicate rows. |
| `all_missing` | A column has no non-missing values. |
| `constant` | A column has at most one non-missing unique value. |
| `near_constant` | The leading non-missing value meets `near_constant_ratio`. |
| `possible_identifier` | Every non-missing value in a column is unique. |
| `high_cardinality` | A categorical column has over 20 values and meets `high_cardinality_ratio`. |
| `high_missing` | Missingness exceeds `missing_threshold`. |
| `numeric_as_string` | At least 90% of text values parse as numbers. |
| `datetime_as_string` | At least 90% of date-like text values parse as datetimes. |
| `potential_outliers` | IQR outlier percentage exceeds `outlier_threshold`. |
| `class_imbalance` | A categorical target meets `imbalance_ratio`. |

`missing_threshold` and `outlier_threshold` use percentage values.
`near_constant_ratio` and `high_cardinality_ratio` must be within `(0, 1]`;
`imbalance_ratio` must exceed one.

## MVP limitations

- pandas `DataFrame` input only; no files, plotting, HTML report, CLI, or
  notebook integration.
- In-memory analysis only; no sampling or distributed execution.
- IQR is the only outlier method and warnings are deterministic heuristics, not
  domain conclusions or automatic cleaning instructions.
- Nested, geospatial, time-series, and mixed object values receive no
  specialized analysis.
- Duplicate column names are rejected rather than repaired.
