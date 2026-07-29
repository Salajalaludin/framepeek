# FramePeek Product Requirements

## Product

FramePeek is a small Python package for repeatable exploratory analysis of
`pandas.DataFrame` objects. It sits between ad-hoc calls such as
`df.describe()` and large HTML profiling systems.

The package helps analysts identify dataset structure and likely quality
problems before cleaning, visualization, statistical analysis, or modeling.
It reports findings but never changes the input data.

## Users

- Data analysts and data scientists
- Students and researchers working with tabular data
- Python users who need consistent, reusable EDA output

## MVP outcome

The MVP is successful when this call returns a complete reusable report:

```python
import framepeek as fp

report = fp.profile(df, target_column="target_column")
```

The report must contain:

| Key | Requirement |
| --- | --- |
| `overview` | Dataset size, missingness, duplicates, memory, and type counts |
| `columns` | Dtype, inferred type, uniqueness, top value, and column flags |
| `missing` | Per-column missing counts, severity, rank, and row completeness |
| `duplicates` | Duplicate totals, groups, and bounded examples |
| `numeric` | Descriptive statistics for numeric columns |
| `categorical` | Frequency, cardinality, and rare-category statistics |
| `outliers` | IQR bounds and potential outlier counts |
| `correlations` | Numeric matrix and tidy correlation pairs |
| `target` | Categorical balance or numeric target analysis |
| `warnings` | Actionable data-quality findings |

Each analysis must also be callable independently through the functional API
documented in the project README.

## Behavioral contract

- Accept only non-empty `pandas.DataFrame` inputs.
- Reject duplicate column names because they make selection ambiguous.
- Reject a requested target or subset column that does not exist.
- Validate method names, thresholds, counts, and multipliers before analysis.
- Never mutate values, dtypes, labels, index, or column order.
- Handle missing and infinite numeric values without crashing.
- Return stable empty schemas when a requested dtype is absent.
- Keep all processing local; never transmit or persist user data.

## Supported analysis

- Missing severity thresholds are configurable.
- Duplicate analysis supports an optional column subset.
- Outliers use the IQR method with a configurable multiplier.
- Correlations support Pearson, Spearman, and Kendall methods.
- Categorical summaries expose configurable top-N and rare-category limits.
- Warning thresholds for missingness, cardinality, outliers, near-constant
  columns, and target imbalance are configurable.

Interpretations are diagnostic signals, not automatic cleaning decisions.

## Non-goals

The MVP does not perform cleaning, imputation, encoding, feature engineering,
modeling, visualization, HTML reporting, database access, distributed
processing, or support non-pandas DataFrames.

Add a capability only when a concrete user workflow requires it.

## Technical constraints

- Python 3.10+
- pandas 2.0+
- `src/` package layout with setuptools
- pandas is the only direct runtime dependency
- Public functions use type hints and docstrings
- Tests must maintain 100% statement coverage
- The package must build as a wheel and install in a clean environment

## Package layout

```text
src/framepeek/
├── __init__.py   # public functional API
└── core.py       # shared validation and analysis implementation

tests/
└── test_mvp.py
```

Split `core.py` only when a real maintenance problem appears; empty modules
for speculative features are not part of the design.

## Acceptance checks

The MVP is releasable when:

1. `python -m pytest --cov=framepeek --cov-fail-under=100` passes.
2. Building a wheel succeeds.
3. Installing that wheel and running `profile()` in a clean environment
   succeeds.
4. The input DataFrame remains unchanged in tests.
5. All report keys and direct functions have documented return shapes.

## Next milestone

After real-world MVP feedback, prioritize only confirmed gaps. Likely
candidates are performance sampling for large DataFrames or machine-readable
report export. A stateful report object, plots, plugins, and additional
DataFrame engines remain out of scope until repeated use justifies them.

The warning-specific 0.2.0 gap analysis is recorded in
[data-quality-0.2-audit.md](data-quality-0.2-audit.md).
