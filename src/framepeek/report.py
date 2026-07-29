"""Profile orchestration and text report formatting."""

from typing import Any

import pandas as pd

from . import analysis
from ._context import AnalysisContext
from .types import (
    ColumnName,
    CorrelationMethod,
    OutlierMethod,
    ProfileResult,
    TargetType,
)
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
    target_type: TargetType = "auto",
    outlier_min_samples: int = 4,
    rare_max_count: int = 1,
    rare_concentration_ratio: float = 0.1,
) -> ProfileResult:
    """Run every MVP analysis without mutating the input DataFrame."""
    validate(df, target_column)
    context = AnalysisContext.from_frame(df)
    outlier_result = analysis.outliers(
        df,
        outlier_method,
        outlier_multiplier,
        min_samples=outlier_min_samples,
        _context=context,
    )
    correlation_result = analysis.correlations(
        df, correlation_method, _context=context
    )
    target_result = (
        analysis.target(
            df,
            target_column,
            imbalance_ratio,
            target_type=target_type,
            _correlation_result=correlation_result,
            _outlier_result=outlier_result,
            _context=context,
        )
        if target_column is not None
        else None
    )
    return {
        "overview": analysis.overview(df, _context=context),
        "columns": analysis.columns(
            df, high_cardinality_ratio, _context=context
        ),
        "missing": analysis.missing(
            df, missing_thresholds, _context=context
        ),
        "duplicates": analysis.duplicates(df),
        "numeric": analysis.numeric(df, _context=context),
        "categorical": analysis.categorical(
            df, top_n_categories, _context=context
        ),
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
            rare_max_count=rare_max_count,
            rare_concentration_ratio=rare_concentration_ratio,
            _outlier_result=outlier_result,
            _target_result=target_result,
            _context=context,
        ),
    }


def print_report(report: ProfileResult | dict[str, Any]) -> None:
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
