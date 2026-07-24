# FramePeek

Lightweight exploratory data analysis for pandas DataFrames.

## Documentation

- [Getting started](docs/getting-started.md)
- [API reference](docs/api-reference.md)
- [Product requirements](docs/PRD.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## Usage

```python
import framepeek as fp

report = fp.profile(
    df,
    target="churn",
    correlation_method="spearman",
    outlier_multiplier=1.5,
    top_n_categories=5,
)
```

The report contains `overview`, `columns`, `missing`, `duplicates`, `numeric`,
`categorical`, `outliers`, `correlations`, `target`, and `warnings`.

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
fp.target(df, target="churn")
fp.warnings(df, target="churn")
```

All functions validate their inputs and leave the original DataFrame unchanged.

## Outputs

| Function | Return value |
| --- | --- |
| `overview` | `DataFrame` of dataset-level metrics |
| `columns` | `DataFrame` with one profile row per column |
| `missing` | `DataFrame`; row totals are stored in `.attrs["rows"]` |
| `duplicates` | Dictionary containing totals, groups, and examples |
| `numeric` | `DataFrame` of descriptive numeric statistics |
| `categorical` | `DataFrame` of frequency and cardinality statistics |
| `outliers` | `DataFrame` of IQR bounds and potential outlier counts |
| `correlations` | Dictionary containing `matrix` and tidy `pairs` tables |
| `target` | Dictionary containing categorical or numeric target analysis |
| `warnings` | `DataFrame` of actionable quality warnings |
| `profile` | Dictionary containing all analyses above |

Thresholds for missingness, cardinality, outliers, correlations, and class
imbalance can be configured through the corresponding function parameters.

## Development

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m mypy src/framepeek
python -m pytest --cov=framepeek --cov-fail-under=100
```
