# API reference

All public functions accept a pandas `DataFrame` with a single-level column
index, validate it, and leave it unchanged. Percentage parameters and output
percentages use the `0..100` scale; ratio parameters use `0..1` unless noted
otherwise. Numeric configuration rejects booleans, `NaN`, and infinity.

The supported public API is exported from `framepeek`. Implementation is
grouped into `analysis`, `validation`, `warnings`, and `report`; configuration
aliases `ColumnName`, `CorrelationMethod`, `OutlierMethod`, and `Severity` are
also public, along with `CorrelationOverflow` and `TargetType`. Modules prefixed
with `_`, including `_context`, are internal and not part of the compatibility
contract.

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
    target_type="auto",
    outlier_min_samples=4,
    rare_max_count=1,
    rare_concentration_ratio=0.1,
    warning_sample_size=1000,
    random_state=0,
    deep_memory=True,
)
```

| Parameter | Meaning |
| --- | --- |
| `df` | Non-empty pandas `DataFrame` with unique column names. |
| `target_column` | Optional existing column name to analyze as the target. |
| `correlation_method` | `pearson`, `spearman`, or `kendall`. |
| `outlier_method` | Outlier method; supports only `iqr`. |
| `outlier_multiplier` | Positive multiplier applied to the IQR bounds. |
| `top_n_categories` | Positive number of leading values retained per categorical column. |
| `missing_thresholds` | Three increasing severity boundaries within `0..100`. |
| `warning_missing_threshold` | Missing percentage above which a warning is emitted. |
| `high_cardinality_ratio` | Categorical unique-value ratio within `(0, 1]`. |
| `imbalance_ratio` | Majority-to-minority ratio above which a target is imbalanced; must exceed `1`. |
| `target_type` | `auto`, `categorical`, or `numeric`; overrides target interpretation when requested. |
| `outlier_min_samples` | Positive minimum finite sample size for the IQR analysis. |
| `rare_max_count` | Maximum frequency considered rare by quality warnings; at least one. |
| `rare_concentration_ratio` | Minimum share of non-null categorical rows in rare categories that triggers a warning; within `(0, 1]`. |
| `warning_sample_size` | Positive maximum number of text values parsed by warning heuristics. |
| `random_state` | Seed used for reproducible warning sampling. |
| `deep_memory` | Whether overview memory usage inspects Python-owned object data. Disable for a faster shallow estimate. |

Returns a dictionary with `metadata`, `overview`, `columns`, `missing`,
`duplicates`, `numeric`, `categorical`, `outliers`, `correlations`, `target`,
and `warnings`. Metadata records versions, configuration, generation time, and
whether warning sampling was used. Report schema remains `1.1`.
`metadata.configuration.warning_sample_size` is the configured upper limit.
`metadata.sampling.warning_sample_size` is the maximum number of non-null values
actually parsed for any categorical column (zero when none were parsed).
`warnings_used` is true only if a categorical column actually needed sampling.

### `format_report(report, *, max_rows=20, max_columns=12, max_colwidth=40)`

Returns bounded text with a title for each top-level section and subheadings
for nested tables. Tables exceeding the supplied limits show ellipses.

### `print_report(report, *, max_rows=20, max_columns=12, max_colwidth=40)`

Prints the same bounded text and returns `None`. Neither formatter changes the
report or global pandas display options.

### `to_serializable(value)`

Returns a JSON-compatible envelope with `schema_version`, `exact`, and `data`.
Serialization schema `1.0` stores DataFrames with explicit index, column, and
data arrays. String-keyed dictionaries remain objects; other mappings use
ordered `key`/`value` entry records, preventing distinct labels such as `1`
and `"1"` from colliding. Tagged values preserve tuples, datetimes, missing
values, non-finite floats, sets, and pandas/NumPy scalars. `exact` is `False`
when an unsupported object can only be represented by its type and display
text.

## Validation and dataset summaries

### `validate(df, target_column=None)`

Validates the shared input rules. Returns `None`. Raises `TypeError` for a
non-DataFrame or MultiIndex columns, `ValueError` for an empty DataFrame or
duplicate column names, and `KeyError` for an unknown target. Duplicate-column
errors include each repeated label and its occurrence count.

### `overview(df, deep_memory=True)`

Returns a two-column `DataFrame` (`metric`, `value`) containing dimensions,
missing and duplicate totals, memory use, and column-type counts.
Set `deep_memory=False` to skip pandas' slower object-data inspection.

### `columns(df, high_cardinality_ratio=0.5)`

Returns one `DataFrame` row per column with dtype, inferred type, completeness,
cardinality, leading value, and identifier/constant/high-cardinality flags.
`high_cardinality_ratio` must be within `(0, 1]`.

### `missing(df, thresholds=(5, 20, 50))`

Returns a `DataFrame` with `column`, `missing`, `missing_pct`, `non_missing`,
`severity`, and `rank` under `result["columns"]`. `result["rows"]` contains
row-level totals, while `result["patterns"]` groups rows by the tuple of columns
that are missing together. `thresholds` must be a tuple of three increasing
values within `0..100`.
Patterns exclude complete rows, sort by descending row count, and preserve
first occurrence when counts tie. Processing uses bounded packed masks, but
the exact output can still grow to one pattern per row. No sampling or
truncation is applied.

### `duplicates(df, subset=None, max_examples=5)`

Returns a dictionary with `duplicate_rows`, `duplicate_pct`,
`duplicate_groups`, `unique_rows`, `groups`, and `examples`. `subset` optionally
selects existing columns; `max_examples` is a non-negative integer. Lists,
dictionaries, sets, and nested mixtures are compared structurally without
changing their display values.

## Column analyses

### `numeric(df)`

Returns one `DataFrame` row per numeric, non-boolean column. It includes count,
missingness, center, spread, quartiles, skewness, kurtosis, zero counts, and
negative-value counts. Returns an empty table with stable columns when there
are no numeric columns.
Missing values and positive/negative infinity are reported separately; summary
statistics use finite values. `coefficient_of_variation` is sample standard
deviation / mean for a positive mean and at least two finite values. It is
`NaN` for zero/negative means or an insufficient sample. Interpret this ratio
only for measurements with a meaningful zero.

### `categorical(df, top_n=5, rare_max_count=1)`

Returns one `DataFrame` row per categorical or boolean column with cardinality,
the leading value, top values, and rare/singleton counts. `top_n` must be a
positive integer and `rare_max_count` must be at least one. String-only top
values retain the compact dictionary form. Other values use records containing
`value`, `count`, and `transformed`; the final field reports whether FramePeek
used a structural or identity key internally.

### `outliers(df, method="iqr", multiplier=1.5, min_samples=4)`

Returns one `DataFrame` row per numeric, non-boolean column with IQR bounds and
potential outlier counts. `method` must be `iqr`; `multiplier` must be positive.
Results are diagnostic and do not remove values.
`applicable` and `limitation` explain insufficient samples or a zero IQR.
In either case, outlier counts, percentages, bounds, and extrema are `NaN`.
Quartiles/IQR remain available for `zero_iqr`. A nonzero IQR, even a small one,
uses the configured bounds without an arbitrary tolerance.

### `correlations`

```python
correlations(
    df,
    method="pearson",
    threshold=0,
    min_periods=2,
    columns=None,
    max_columns=50,
    overflow="error",
    include_matrix=True,
    top_pairs=None,
    sample_rows=None,
    random_state=0,
)
```

Returns `{"matrix": DataFrame, "pairs": DataFrame}` for numeric, non-boolean
columns. `method` accepts `pearson`, `spearman`, or `kendall`; `threshold`
filters pairs by absolute correlation and must be within `0..1`. `columns`
selects a subset, while `max_columns` limits work and `overflow="skip"` returns
empty tables instead of raising. Set `include_matrix=False` for pair-only output
and `top_pairs` to retain only the strongest pairs. `sample_rows` performs
reproducible row sampling. Kendall on more than 10,000 rows requires
`sample_rows`.
`profile()` does not expose these controls: its correlation calculation retains
the defaults, including the 50-column limit. Use the standalone function for
larger selections or sampled Kendall analysis.

Correlation strength labels are descriptive heuristics, not universal
statistical rules; interpretation depends on the domain and sample.

### `target(df, target_column, imbalance_ratio=3, *, target_type="auto")`

Analyzes an existing target column. Targets with at most 20 non-missing unique
values, plus categorical and boolean targets, return a categorical dictionary
with distribution and imbalance fields. Other numeric targets return a
dictionary with numeric summary, outliers, and correlations. Set `target_type`
to override automatic interpretation.
`imbalance_ratio` must exceed one.

## Warnings

### `quality_warnings`

```python
quality_warnings(
    df,
    target_column=None,
    missing_threshold=20,
    near_constant_ratio=0.95,
    high_cardinality_ratio=0.5,
    outlier_threshold=5,
    imbalance_ratio=3,
    rare_max_count=1,
    rare_concentration_ratio=0.1,
    sample_size=1000,
    random_state=0,
    *,
    outlier_method="iqr",
    outlier_multiplier=1.5,
)
```

Returns a `DataFrame` with `code`, `severity`, `column`, `message`,
`recommendation`, and `metric`.
`warnings()` remains a compatibility alias; new code should use
`quality_warnings()`.

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
| `non_finite_values` | A numeric column contains positive or negative infinity. |
| `numeric_identifier` | At least 90% of sampled text parses numerically, and either more than 50% has a leading zero or all non-null values are unique with sampled text of the same length (at least five characters). |
| `empty_string` | Text contains empty or whitespace-only values. |
| `surrounding_whitespace` | Text contains leading or trailing whitespace. |
| `category_case` | Categories differ only by letter case. |
| `mixed_object_types` | An object column contains mixed Python value types. |
| `rare_category_concentration` | Rare categories collectively meet the configured row-share ratio. |

`missing_threshold` and `outlier_threshold` use percentage values.
`near_constant_ratio` and `high_cardinality_ratio` must be within `(0, 1]`;
`imbalance_ratio` must exceed one. Text parsing uses at most `sample_size`
randomly selected values and is reproducible with `random_state`.

## Limitations

- pandas `DataFrame` input only; no files, plotting, HTML report, CLI, or
  notebook integration.
- In-memory analysis only; sampling is limited to text-warning heuristics and
  optional correlation rows; no distributed execution.
- IQR is the only outlier method and warnings are deterministic heuristics, not
  domain conclusions or automatic cleaning instructions.
- Nested, geospatial, time-series, and mixed object values receive no
  specialized analysis.
- Duplicate column names are rejected rather than repaired.
