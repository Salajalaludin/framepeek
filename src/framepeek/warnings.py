"""Data-quality warning analysis."""

from typing import Any, cast

import pandas as pd

from . import analysis
from ._context import AnalysisContext
from .types import (
    ColumnName,
    OutlierMethod,
    Severity,
    TargetResult,
    WarningsResult,
)
from .validation import _number, validate

_WARNING_COLUMNS = [
    "code",
    "severity",
    "column",
    "message",
    "recommendation",
    "metric",
]


def warnings(
    df: pd.DataFrame,
    target_column: ColumnName | None = None,
    missing_threshold: float = 20,
    near_constant_ratio: float = 0.95,
    high_cardinality_ratio: float = 0.5,
    outlier_threshold: float = 5,
    imbalance_ratio: float = 3,
    *,
    outlier_method: OutlierMethod = "iqr",
    outlier_multiplier: float = 1.5,
    _outlier_result: pd.DataFrame | None = None,
    _target_result: TargetResult | None = None,
    _context: AnalysisContext | None = None,
) -> WarningsResult:
    """Return actionable data-quality warnings."""
    validate(df, target_column)
    _number("missing_threshold", missing_threshold, minimum=0, maximum=100)
    _number(
        "outlier_threshold",
        outlier_threshold,
        minimum=0,
        maximum=100,
        include_minimum=False,
    )
    _number(
        "near_constant_ratio",
        near_constant_ratio,
        minimum=0,
        maximum=1,
        include_minimum=False,
    )
    _number(
        "high_cardinality_ratio",
        high_cardinality_ratio,
        minimum=0,
        maximum=1,
        include_minimum=False,
    )

    context = _context or AnalysisContext.from_frame(df)
    rows: list[dict[str, Any]] = []

    def add(
        code: str,
        severity: Severity,
        column: ColumnName | None,
        message: str,
        recommendation: str,
        metric: float | int,
    ) -> None:
        rows.append(
            {
                "code": code,
                "severity": severity,
                "column": column,
                "message": message,
                "recommendation": recommendation,
                "metric": metric,
            }
        )

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        add(
            "duplicate_rows",
            "medium",
            None,
            f"Dataset contains {duplicate_count} duplicate rows.",
            "Review duplicate rows before analysis.",
            duplicate_count,
        )

    for name in df.columns:
        series = df[name]
        metadata = context.columns[name]
        non_null = series.dropna()
        unique = metadata.unique
        missing_pct = analysis._pct(metadata.missing, len(series))
        if not len(non_null):
            add(
                "all_missing",
                "critical",
                name,
                f"Column {name!r} contains only missing values.",
                "Remove the column or restore its source data.",
                100,
            )
            continue
        if unique <= 1:
            add(
                "constant",
                "high",
                name,
                f"Column {name!r} has no variation.",
                "Exclude it from analyses that require variation.",
                unique,
            )
        else:
            top_ratio = float(metadata.value_counts.iloc[0] / metadata.non_null)
            if top_ratio >= near_constant_ratio:
                add(
                    "near_constant",
                    "medium",
                    name,
                    f"Column {name!r} is nearly constant.",
                    "Check whether the rare values are meaningful.",
                    round(top_ratio, 4),
                )
        if unique == len(non_null):
            add(
                "possible_identifier",
                "medium",
                name,
                f"Column {name!r} contains only unique non-missing values.",
                "Treat it as an identifier unless it is a measured feature.",
                unique,
            )
        ratio = unique / len(non_null)
        if (
            analysis._kind(series) == "categorical"
            and unique > 20
            and ratio >= high_cardinality_ratio
        ):
            add(
                "high_cardinality",
                "medium",
                name,
                f"Column {name!r} has high categorical cardinality.",
                "Review identifiers and rare categories.",
                round(ratio, 4),
            )
        if missing_pct > missing_threshold:
            add(
                "high_missing",
                "critical" if missing_pct > 50 else "high",
                name,
                f"Column {name!r} contains {missing_pct}% missing values.",
                "Investigate the missing-data mechanism.",
                missing_pct,
            )
        if metadata.kind == "categorical":
            text = non_null.astype(str)
            numeric_ratio = float(pd.to_numeric(text, errors="coerce").notna().mean())
            if numeric_ratio >= 0.9:
                add(
                    "numeric_as_string",
                    "medium",
                    name,
                    f"Column {name!r} appears numeric but is stored as text.",
                    "Validate and convert it to a numeric dtype.",
                    round(numeric_ratio, 4),
                )
            elif text.str.contains(r"[-/:]", regex=True).mean() >= 0.9:
                date_ratio = float(
                    pd.to_datetime(text, errors="coerce", format="mixed")
                    .notna()
                    .mean()
                )
                if date_ratio >= 0.9:
                    add(
                        "datetime_as_string",
                        "medium",
                        name,
                        f"Column {name!r} appears to contain datetimes.",
                        "Validate and convert it to a datetime dtype.",
                        round(date_ratio, 4),
                    )

    outlier_result = (
        _outlier_result
        if _outlier_result is not None
        else analysis.outliers(df, outlier_method, outlier_multiplier)
    )
    for row in outlier_result.itertuples(index=False):
        outlier_pct = cast(float, row.outlier_pct)
        if pd.notna(outlier_pct) and outlier_pct > outlier_threshold:
            add(
                "potential_outliers",
                "medium",
                row.column,
                f"Column {row.column!r} contains {outlier_pct}% potential outliers.",
                "Review them in domain context; do not remove automatically.",
                outlier_pct,
            )

    if target_column is not None:
        target_result = _target_result or analysis.target(
            df, target_column, imbalance_ratio
        )
        if target_result["type"] == "categorical" and target_result["imbalanced"]:
            ratio = target_result["majority_to_minority_ratio"]
            add(
                "class_imbalance",
                "high",
                target_column,
                f"Target {target_column!r} has a majority-to-minority ratio of {ratio}.",
                "Use stratified evaluation and imbalance-aware metrics.",
                ratio,
            )
    return pd.DataFrame(rows, columns=_WARNING_COLUMNS)
