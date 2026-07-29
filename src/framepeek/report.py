"""Profile orchestration and text report formatting."""

from datetime import datetime, timezone
from importlib.metadata import version
from platform import python_version
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
from .warnings import quality_warnings


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
    warning_sample_size: int = 1000,
    random_state: int = 0,
    deep_memory: bool = True,
) -> ProfileResult:
    """Run every MVP analysis without mutating the input DataFrame."""
    validate(df, target_column)
    if not isinstance(deep_memory, bool):
        raise TypeError("deep_memory must be a boolean.")
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
        "metadata": {
            "schema_version": "1.1",
            "framepeek_version": version("framepeek"),
            "pandas_version": pd.__version__,
            "python_version": python_version(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "correlation_method": correlation_method,
                "outlier_method": outlier_method,
                "outlier_multiplier": outlier_multiplier,
                "target_type": target_type,
                "warning_sample_size": warning_sample_size,
                "random_state": random_state,
                "deep_memory": deep_memory,
            },
            "sampling": {
                "warnings_used": len(df) > warning_sample_size
                and any(
                    metadata.kind == "categorical"
                    for metadata in context.columns.values()
                ),
                "warning_sample_size": min(len(df), warning_sample_size),
                "random_state": random_state,
            },
        },
        "overview": analysis.overview(df, deep_memory, _context=context),
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
        "warnings": quality_warnings(
            df,
            target_column=target_column,
            missing_threshold=warning_missing_threshold,
            high_cardinality_ratio=high_cardinality_ratio,
            imbalance_ratio=imbalance_ratio,
            outlier_method=outlier_method,
            outlier_multiplier=outlier_multiplier,
            rare_max_count=rare_max_count,
            rare_concentration_ratio=rare_concentration_ratio,
            sample_size=warning_sample_size,
            random_state=random_state,
            _outlier_result=outlier_result,
            _target_result=target_result,
            _context=context,
        ),
    }


def format_report(
    report: ProfileResult | dict[str, Any],
    *,
    max_rows: int = 20,
    max_columns: int = 12,
    max_colwidth: int = 40,
) -> str:
    """Format a bounded text report."""
    if not isinstance(report, dict):
        raise TypeError("report must be the dictionary returned by profile().")

    lines: list[str] = []

    def format_value(value: Any) -> None:
        if isinstance(value, pd.DataFrame):
            lines.append(
                value.to_string(
                    index=False,
                    max_rows=max_rows,
                    max_cols=max_columns,
                    line_width=None,
                    max_colwidth=max_colwidth,
                )
            )
        elif isinstance(value, dict):
            for key, nested in value.items():
                if isinstance(nested, (dict, pd.DataFrame)):
                    lines.append(f"\n--- {str(key).replace('_', ' ').upper()} ---")
                    format_value(nested)
                else:
                    lines.append(f"{key}: {nested}")
        else:
            lines.append(str(value))

    for section, value in report.items():
        lines.append(f"\n=== {str(section).replace('_', ' ').upper()} ===")
        format_value(value)
    return "\n".join(lines)


def print_report(
    report: ProfileResult | dict[str, Any],
    *,
    max_rows: int = 20,
    max_columns: int = 12,
    max_colwidth: int = 40,
) -> None:
    """Print a bounded formatted report."""
    print(
        format_report(
            report,
            max_rows=max_rows,
            max_columns=max_columns,
            max_colwidth=max_colwidth,
        )
    )
