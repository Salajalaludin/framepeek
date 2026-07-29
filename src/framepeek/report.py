"""Profile orchestration and text report formatting."""

from typing import Any

import pandas as pd

from . import analysis
from .types import ColumnName, CorrelationMethod, OutlierMethod
from .validation import validate
from .warnings import warnings


def profile(
    df: pd.DataFrame,
    target_column: ColumnName | None = None,
    correlation_method: CorrelationMethod = "pearson",
    outlier_method: OutlierMethod = "iqr",
    outlier_multiplier: float = 1.5,
    top_n_categories: int = 5,
    missing_thresholds: tuple[float, float, float] = (5, 20, 50),
    warning_missing_threshold: float = 20,
    high_cardinality_ratio: float = 0.5,
    imbalance_ratio: float = 3,
) -> dict[str, Any]:
    """Run every MVP analysis without mutating the input DataFrame."""
    validate(df, target_column)
    outlier_result = analysis.outliers(
        df, outlier_method, outlier_multiplier
    )
    correlation_result = analysis.correlations(df, correlation_method)
    target_result = (
        analysis.target(
            df,
            target_column,
            imbalance_ratio,
            _correlation_result=correlation_result,
            _outlier_result=outlier_result,
        )
        if target_column is not None
        else None
    )
    return {
        "overview": analysis.overview(df),
        "columns": analysis.columns(df, high_cardinality_ratio),
        "missing": analysis.missing(df, missing_thresholds),
        "duplicates": analysis.duplicates(df),
        "numeric": analysis.numeric(df),
        "categorical": analysis.categorical(df, top_n_categories),
        "outliers": outlier_result,
        "correlations": correlation_result,
        "target": target_result,
        "warnings": warnings(
            df,
            target_column=target_column,
            missing_threshold=warning_missing_threshold,
            high_cardinality_ratio=high_cardinality_ratio,
            imbalance_ratio=imbalance_ratio,
            outlier_method=outlier_method,
            outlier_multiplier=outlier_multiplier,
            _outlier_result=outlier_result,
            _target_result=target_result,
        ),
    }


def print_report(report: dict[str, Any]) -> None:
    """Print a profile report with titled, untruncated tables."""
    if not isinstance(report, dict):
        raise TypeError("report must be the dictionary returned by profile().")

    def print_value(value: Any) -> None:
        if isinstance(value, pd.DataFrame):
            print(
                value.to_string(
                    index=False,
                    max_rows=None,
                    max_cols=None,
                    line_width=None,
                    max_colwidth=None,
                )
            )
        elif isinstance(value, dict):
            for key, nested in value.items():
                if isinstance(nested, (dict, pd.DataFrame)):
                    print(f"\n--- {str(key).replace('_', ' ').upper()} ---")
                    print_value(nested)
                else:
                    print(f"{key}: {nested}")
        else:
            print(value)

    for section, value in report.items():
        print(f"\n=== {str(section).replace('_', ' ').upper()} ===")
        print_value(value)
