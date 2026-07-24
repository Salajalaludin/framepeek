# Getting started

FramePeek produces a compact exploratory data analysis report from a pandas
DataFrame without modifying the input.

## Install

Install FramePeek with Python 3.10 or newer:

```bash
python -m pip install framepeek
```

For local development, clone the repository and use an editable install:

```bash
git clone https://github.com/Salajalaludin/framepeek.git
cd framepeek
python -m pip install -e .
```

## Create a report

```python
import pandas as pd
import framepeek as fp

df = pd.DataFrame(
    {
        "age": [24, 31, 31, None],
        "plan": ["free", "pro", "pro", "free"],
        "churn": ["no", "no", "yes", "yes"],
    }
)

report = fp.profile(df, target="churn")

fp.print_report(report)
```

`profile()` returns ten sections: `overview`, `columns`, `missing`,
`duplicates`, `numeric`, `categorical`, `outliers`, `correlations`, `target`,
and `warnings`. `print_report()` prints each section under a title without
truncating rows, columns, or long values. The `target` value is `None` when no
target column is supplied.

Use an individual analysis when the full report is unnecessary:

```python
missing_by_column = fp.missing(df, thresholds=(5, 20, 50))
strong_pairs = fp.correlations(df, method="spearman", threshold=0.7)
```

## Input rules

- Input must be a non-empty pandas `DataFrame` with at least one column.
- Column names must be unique.
- A supplied target must match an existing column name.
- Missing values and datasets without a particular supported column type are
  handled by returning empty or missing-aware results.
- FramePeek does not alter the source DataFrame.

See the [API reference](api-reference.md) for parameters, output shapes,
warning codes, and MVP limitations.
