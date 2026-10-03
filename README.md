# FramePeek

Lightweight exploratory data analysis for pandas DataFrames.

## Documentation

- [Getting started](https://github.com/Salajalaludin/framepeek/blob/main/docs/getting-started.md)
- [API reference](https://github.com/Salajalaludin/framepeek/blob/main/docs/api-reference.md)
- [Product requirements](https://github.com/Salajalaludin/framepeek/blob/main/docs/PRD.md)
- [Changelog](https://github.com/Salajalaludin/framepeek/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/Salajalaludin/framepeek/blob/main/CONTRIBUTING.md)
- [Code of Conduct](https://github.com/Salajalaludin/framepeek/blob/main/CODE_OF_CONDUCT.md)
- [Release guide](https://github.com/Salajalaludin/framepeek/blob/main/docs/FramePeek%20Release%20Workflow.md)

## Usage

```python
import framepeek as fp

report = fp.profile(
    df,
    target_column="churn",
    correlation_method="spearman",
    outlier_multiplier=1.5,
    top_n_categories=5,
)

fp.print_report(report)
```

The report contains `metadata`, `overview`, `columns`, `missing`, `duplicates`, `numeric`,
`categorical`, `outliers`, `correlations`, `target`, and `warnings`.
`print_report()` gives each section a title and limits table output to 20 rows,
12 columns, and 40 characters per cell by default. Increase `max_rows`,
`max_columns`, and `max_colwidth` when you need more detail.

Each analysis is also available directly:

```python
fp.overview(df)
fp.columns(df)
fp.missing(df)
fp.duplicates(df)
fp.numeric(df)
fp.categorical(df)
fp.outliers(df)
fp.correlations(df)
fp.target(df, target_column="churn")
fp.quality_warnings(df, target_column="churn")
```

All functions validate their inputs and leave the original DataFrame unchanged.
Object columns containing lists, tuples, dictionaries, sets, frozensets, or
NumPy arrays use recursive structural identity for duplicate and categorical
analysis. Arrays match when their concrete type, shape, dtype, and nested values
match. Other unhashable custom objects use scalar boolean equality; objects
whose equality raises or returns a non-scalar result are treated as distinct
unless they are the same instance. Cyclic references likewise use instance
identity at the cycle boundary.

## Outputs

| Function | Return value |
| --- | --- |
| `overview` | `DataFrame` of dataset-level metrics |
| `columns` | `DataFrame` with one profile row per column |
| `missing` | Dictionary containing explicit `columns`, `rows`, and co-missingness `patterns` |
| `duplicates` | Dictionary containing totals, groups, and examples |
| `numeric` | `DataFrame` of descriptive numeric statistics |
| `categorical` | `DataFrame` of frequency and cardinality statistics |
| `outliers` | `DataFrame` of IQR bounds and potential outlier counts |
| `correlations` | Dictionary containing `matrix` and tidy `pairs` tables |
| `target` | Dictionary containing categorical or numeric target analysis |
| `quality_warnings` | `DataFrame` of actionable quality warnings |
| `profile` | Dictionary containing metadata and all analyses above |
| `format_report` | Bounded text representation of a profile |
| `print_report` | `None`; prints the bounded text representation |
| `to_serializable` | Versioned JSON-compatible envelope preserving table labels and conversion fidelity |

Thresholds for missingness, cardinality, outliers, correlations, and class
imbalance can be configured through the corresponding function parameters.
Warning text parsing is sampled reproducibly for large columns. Correlation
analysis supports column subsets, limits, pair-only output, top pairs, and
reproducible row sampling.
Those correlation controls belong to `correlations()`; `profile()` retains the
50 numeric-column limit and the 10,000-row limit for unsampled Kendall.
Missing patterns remain exact and untruncated, so the returned table can still
be large when many rows have different missing-column combinations.

Numeric statistics exclude infinity separately from missing values. Coefficient
of variation is sample standard deviation divided by a positive mean; it is
`NaN` for zero/negative means or fewer than two finite values. Non-applicable
IQR analyses return `NaN` outlier measurements, not a claim of zero outliers.
Sampling metadata records actual text parsing: whether any column was sampled
and the largest number of values parsed for one column, or zero if none.
Serialization schema `1.0` stores DataFrames as explicit index, column, and
data arrays. Mappings with non-string keys use entry records so distinct labels
cannot overwrite each other; the envelope's `exact` field identifies lossy
fallback display values.
`warnings()` remains available as a compatibility alias. Pass
`deep_memory=False` to `overview()` or `profile()` when a shallow memory
estimate is sufficient.

Run the bounded runtime and peak-memory smoke benchmarks with:

```bash
python benchmarks/benchmark_profile.py
# Include the one-million-row numeric and missingness cases:
python benchmarks/benchmark_profile.py --large
```

## Development

```bash
python -m pip install -e ".[dev,release]"
python -m ruff check .
python -m mypy src/framepeek
python -m pytest --cov=framepeek --cov-branch --cov-fail-under=100
python -m build --outdir dist/check
python -m twine check --strict dist/check/*
python scripts/verify_artifacts.py dist/check
```

Use a fresh artifact directory for each build. The artifact verifier checks
archive contents, installs the wheel and sdist in separate new environments,
validates report/serialization schemas, and checks a typed public consumer.
