# FramePeek

Lightweight exploratory data analysis for pandas DataFrames.

## Documentation

- [Getting started](https://github.com/Salajalaludin/framepeek/blob/main/docs/getting-started.md)
- [API reference](https://github.com/Salajalaludin/framepeek/blob/main/docs/api-reference.md)
- [Product requirements](https://github.com/Salajalaludin/framepeek/blob/main/docs/PRD.md)
- [Changelog](https://github.com/Salajalaludin/framepeek/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/Salajalaludin/framepeek/blob/main/CONTRIBUTING.md)
- [Code of Conduct](https://github.com/Salajalaludin/framepeek/blob/main/CODE_OF_CONDUCT.md)
- [Release guide](https://github.com/Salajalaludin/framepeek/blob/main/docs/releasing.md)

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

The report contains `overview`, `columns`, `missing`, `duplicates`, `numeric`,
`categorical`, `outliers`, `correlations`, `target`, and `warnings`.
`print_report()` gives each section a title and prints tables without
formatter-generated ellipses.

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
```

## Development

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m mypy src/framepeek
python -m pytest --cov=framepeek --cov-fail-under=100
```
