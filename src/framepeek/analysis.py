"""Dataset and column analysis functions."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations
from math import inf, nan
from typing import Any, Literal, cast, overload

import pandas as pd

from ._context import AnalysisContext, column_kind
from .types import (
    CategoricalTargetResult,
    ColumnName,
    CorrelationMethod,
    CorrelationOverflow,
    CorrelationResult,
    DuplicatesResult,
    MissingResult,
    MissingRowsResult,
    NumericTargetResult,
    OutlierMethod,
    TargetResult,
    TargetType,
)
from .validation import _choice, _integer, _number, validate


def _pct(value: int | float, total: int) -> float:
    return round(float(value) / total * 100, 2) if total else 0.0


_kind = column_kind


def _get_context(
    df: pd.DataFrame,
    context: AnalysisContext | None,
) -> AnalysisContext:
    return context or AnalysisContext.from_frame(df)


def overview(
    df: pd.DataFrame,
    *,
    _context: AnalysisContext | None = None,
) -> pd.DataFrame:
    """Return dataset-level size, quality, memory, and type metrics."""
    validate(df)
    rows, column_count = df.shape
    total_cells = rows * column_count
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    context = _get_context(df, _context)
    kinds = pd.Series(
        [metadata.kind for metadata in context.columns.values()]
    ).value_counts()
    metrics = {
        "rows": rows,
        "columns": column_count,
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_pct": _pct(missing_cells, total_cells),
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": _pct(duplicate_rows, rows),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 4),
        "numeric_columns": int(kinds.get("numeric", 0)),
        "categorical_columns": int(kinds.get("categorical", 0)),
        "boolean_columns": int(kinds.get("boolean", 0)),
        "datetime_columns": int(kinds.get("datetime", 0)),
        "other_columns": int(kinds.get("other", 0)),
    }
    return pd.DataFrame(metrics.items(), columns=["metric", "value"])


def columns(
    df: pd.DataFrame,
    high_cardinality_ratio: float = 0.5,
    *,
    _context: AnalysisContext | None = None,
) -> pd.DataFrame:
    """Return one structural and quality summary row per column."""
    validate(df)
    _number(
        "high_cardinality_ratio",
        high_cardinality_ratio,
        minimum=0,
        maximum=1,
        include_minimum=False,
    )

    context = _get_context(df, _context)
    rows: list[dict[str, Any]] = []
    for name in df.columns:
        series = df[name]
        metadata = context.columns[name]
        non_null, unique = metadata.non_null, metadata.unique
        counts = metadata.value_counts
        top = counts.index[0] if not counts.empty else None
        top_frequency = int(counts.iloc[0]) if not counts.empty else 0
        kind = metadata.kind
        unique_ratio = unique / non_null if non_null else 0.0
        rows.append(
            {
                "column": name,
                "dtype": str(series.dtype),
                "inferred_type": kind,
                "non_null": non_null,
                "missing": len(series) - non_null,
                "missing_pct": _pct(len(series) - non_null, len(series)),
                "unique": unique,
                "unique_pct": round(unique_ratio * 100, 2),
                "top": top,
                "top_frequency": top_frequency,
                "top_pct": _pct(top_frequency, non_null),
                "possible_id": bool(non_null and unique == non_null),
                "constant": unique <= 1,
                "high_cardinality": bool(
                    kind == "categorical"
                    and unique > 20
                    and unique_ratio >= high_cardinality_ratio
                ),
            }
        )
    return pd.DataFrame(rows)


def missing(
    df: pd.DataFrame,
    thresholds: tuple[float, float, float] = (5, 20, 50),
    *,
    _context: AnalysisContext | None = None,
) -> MissingResult:
    """Return explicit column and row missingness summaries."""
    validate(df)
    if not isinstance(thresholds, tuple) or len(thresholds) != 3:
        raise ValueError("thresholds must contain exactly three values.")
    low, moderate, high = (
        _number(f"thresholds[{index}]", value, minimum=0, maximum=100)
        for index, value in enumerate(thresholds)
    )
    if not low < moderate < high:
        raise ValueError("thresholds must be strictly increasing.")

    context = _get_context(df, _context)
    counts = pd.Series(
        {name: metadata.missing for name, metadata in context.columns.items()}
    )
    result = pd.DataFrame(
        {
            "column": df.columns,
            "missing": counts.to_numpy(dtype=int),
            "missing_pct": [_pct(value, len(df)) for value in counts],
            "non_missing": (len(df) - counts).to_numpy(dtype=int),
        }
    )

    def severity(value: float) -> str:
        if value == 0:
            return "none"
        if value <= low:
            return "low"
        if value <= moderate:
            return "moderate"
        if value <= high:
            return "high"
        return "critical"

    result["severity"] = result["missing_pct"].map(severity)
    result["rank"] = result["missing"].rank(method="min", ascending=False).astype(int)
    incomplete = int(df.isna().any(axis=1).sum())
    row_summary: MissingRowsResult = {
        "rows_with_missing": incomplete,
        "complete_rows": len(df) - incomplete,
        "complete_rows_pct": _pct(len(df) - incomplete, len(df)),
    }
    return {
        "columns": result.sort_values(
            "missing", ascending=False, kind="stable"
        ).reset_index(drop=True),
        "rows": row_summary,
    }


def duplicates(
    df: pd.DataFrame,
    subset: Sequence[ColumnName] | None = None,
    max_examples: int = 5,
) -> DuplicatesResult:
    """Return duplicate totals, repeated groups, and bounded examples."""
    validate(df)
    _integer("max_examples", max_examples, minimum=0)
    if subset is not None:
        unknown = [name for name in subset if name not in df.columns]
        if unknown:
            raise KeyError(f"Subset columns were not found: {unknown!r}.")
        if not subset:
            raise ValueError("subset must contain at least one column.")

    duplicate_rows = int(df.duplicated(subset=subset).sum())
    repeated = df[df.duplicated(subset=subset, keep=False)]
    keys = list(subset) if subset is not None else list(df.columns)
    if repeated.empty:
        groups = pd.DataFrame(columns=[*keys, "count"])
    else:
        groups = (
            repeated.groupby(keys, dropna=False, sort=False)
            .size()
            .rename("count")
            .reset_index()
            .sort_values("count", ascending=False)
            .reset_index(drop=True)
        )
    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": _pct(duplicate_rows, len(df)),
        "duplicate_groups": len(groups),
        "unique_rows": len(df) - duplicate_rows,
        "groups": groups,
        "examples": repeated.head(max_examples).copy(),
    }


_NUMERIC_COLUMNS = [
    "column",
    "count",
    "missing",
    "missing_pct",
    "non_finite",
    "non_finite_pct",
    "positive_infinity",
    "negative_infinity",
    "mean",
    "median",
    "mode",
    "std",
    "variance",
    "min",
    "max",
    "range",
    "q1",
    "q2",
    "q3",
    "iqr",
    "coefficient_of_variation",
    "skewness",
    "kurtosis",
    "zero_count",
    "zero_pct",
    "negative_count",
    "negative_pct",
]


def numeric(
    df: pd.DataFrame,
    *,
    _context: AnalysisContext | None = None,
) -> pd.DataFrame:
    """Return descriptive statistics for numeric, non-boolean columns."""
    validate(df)
    context = _get_context(df, _context)
    rows: list[dict[str, Any]] = []
    for name in context.numeric_names:
        series = df[name]
        positive_infinity = int(series.eq(inf).sum())
        negative_infinity = int(series.eq(-inf).sum())
        non_finite = positive_infinity + negative_infinity
        clean = series.replace([inf, -inf], nan).dropna()
        count = len(clean)
        mode = clean.mode()
        mean = clean.mean() if count else nan
        std = clean.std() if count > 1 else nan
        q1 = clean.quantile(0.25) if count else nan
        q2 = clean.quantile(0.5) if count else nan
        q3 = clean.quantile(0.75) if count else nan
        zero_count = int(clean.eq(0).sum())
        negative_count = int(clean.lt(0).sum())
        rows.append(
            {
                "column": name,
                "count": count,
                "missing": context.columns[name].missing,
                "missing_pct": _pct(context.columns[name].missing, len(df)),
                "non_finite": non_finite,
                "non_finite_pct": _pct(non_finite, len(df)),
                "positive_infinity": positive_infinity,
                "negative_infinity": negative_infinity,
                "mean": mean,
                "median": q2,
                "mode": mode.iloc[0] if not mode.empty else nan,
                "std": std,
                "variance": clean.var() if count > 1 else nan,
                "min": clean.min() if count else nan,
                "max": clean.max() if count else nan,
                "range": clean.max() - clean.min() if count else nan,
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "iqr": q3 - q1,
                "coefficient_of_variation": (
                    std / mean if count > 1 and mean != 0 else nan
                ),
                "skewness": clean.skew() if count > 2 else nan,
                "kurtosis": clean.kurt() if count > 3 else nan,
                "zero_count": zero_count,
                "zero_pct": _pct(zero_count, count),
                "negative_count": negative_count,
                "negative_pct": _pct(negative_count, count),
            }
        )
    return pd.DataFrame(rows, columns=_NUMERIC_COLUMNS)


_CATEGORICAL_COLUMNS = [
    "column",
    "unique",
    "missing",
    "missing_pct",
    "top",
    "top_frequency",
    "top_pct",
    "cardinality_ratio",
    "top_categories",
    "rare_categories",
    "singleton_categories",
]


def categorical(
    df: pd.DataFrame,
    top_n: int = 5,
    rare_max_count: int = 1,
    *,
    _context: AnalysisContext | None = None,
) -> pd.DataFrame:
    """Return frequency and cardinality summaries for categorical columns."""
    validate(df)
    _integer("top_n", top_n, minimum=1)
    _integer("rare_max_count", rare_max_count, minimum=1)
    context = _get_context(df, _context)
    rows: list[dict[str, Any]] = []
    for name in df.columns:
        series = df[name]
        metadata = context.columns[name]
        if metadata.kind not in {"categorical", "boolean"}:
            continue
        counts = metadata.value_counts
        non_null, unique = metadata.non_null, metadata.unique
        rows.append(
            {
                "column": name,
                "unique": unique,
                "missing": len(series) - non_null,
                "missing_pct": _pct(len(series) - non_null, len(series)),
                "top": counts.index[0] if not counts.empty else None,
                "top_frequency": int(counts.iloc[0]) if not counts.empty else 0,
                "top_pct": _pct(int(counts.iloc[0]), non_null)
                if not counts.empty
                else 0.0,
                "cardinality_ratio": round(unique / non_null, 4)
                if non_null
                else 0.0,
                "top_categories": counts.head(top_n).to_dict(),
                "rare_categories": int(counts.le(rare_max_count).sum()),
                "singleton_categories": int(counts.eq(1).sum()),
            }
        )
    return pd.DataFrame(rows, columns=_CATEGORICAL_COLUMNS)


_OUTLIER_COLUMNS = [
    "column",
    "q1",
    "q3",
    "iqr",
    "lower_bound",
    "upper_bound",
    "outlier_count",
    "outlier_pct",
    "lower_outliers",
    "upper_outliers",
    "min_outlier",
    "max_outlier",
    "sample_size",
    "applicable",
    "limitation",
]


def outliers(
    df: pd.DataFrame,
    method: OutlierMethod = "iqr",
    multiplier: float = 1.5,
    min_samples: int = 4,
    *,
    _context: AnalysisContext | None = None,
) -> pd.DataFrame:
    """Return IQR-based potential outlier summaries for numeric columns."""
    validate(df)
    _choice("method", method, {"iqr"})
    _number("multiplier", multiplier, minimum=0, include_minimum=False)
    _integer("min_samples", min_samples, minimum=1)
    context = _get_context(df, _context)
    rows: list[dict[str, Any]] = []
    for name in context.numeric_names:
        clean = df[name].replace([inf, -inf], nan).dropna()
        if len(clean) < min_samples:
            rows.append(
                {
                    "column": name,
                    "sample_size": len(clean),
                    "applicable": False,
                    "limitation": "insufficient_sample",
                }
            )
            continue
        q1, q3 = clean.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            rows.append(
                {
                    "column": name,
                    "q1": q1,
                    "q3": q3,
                    "iqr": iqr,
                    "outlier_count": 0,
                    "outlier_pct": 0.0,
                    "lower_outliers": 0,
                    "upper_outliers": 0,
                    "sample_size": len(clean),
                    "applicable": False,
                    "limitation": "zero_iqr",
                }
            )
            continue
        lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
        lower_values, upper_values = clean[clean < lower], clean[clean > upper]
        values = pd.concat([lower_values, upper_values])
        rows.append(
            {
                "column": name,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_bound": lower,
                "upper_bound": upper,
                "outlier_count": len(values),
                "outlier_pct": _pct(len(values), len(clean)),
                "lower_outliers": len(lower_values),
                "upper_outliers": len(upper_values),
                "min_outlier": values.min() if not values.empty else nan,
                "max_outlier": values.max() if not values.empty else nan,
                "sample_size": len(clean),
                "applicable": True,
                "limitation": None,
            }
        )
    return pd.DataFrame(rows, columns=_OUTLIER_COLUMNS)


def _strength(value: float) -> str:
    if value < 0.2:
        return "very weak"
    if value < 0.4:
        return "weak"
    if value < 0.6:
        return "moderate"
    if value < 0.8:
        return "strong"
    return "very strong"


_CORRELATION_PAIR_COLUMNS = [
    "column_1",
    "column_2",
    "correlation",
    "absolute_correlation",
    "direction",
    "strength",
]


def correlations(
    df: pd.DataFrame,
    method: CorrelationMethod = "pearson",
    threshold: float = 0,
    min_periods: int = 2,
    columns: Sequence[ColumnName] | None = None,
    max_columns: int = 50,
    overflow: CorrelationOverflow = "error",
    include_matrix: bool = True,
    top_pairs: int | None = None,
    sample_rows: int | None = None,
    random_state: int = 0,
    *,
    _context: AnalysisContext | None = None,
) -> CorrelationResult:
    """Return a numeric correlation matrix and a tidy pair table."""
    validate(df)
    _choice("method", method, {"pearson", "spearman", "kendall"})
    _number("threshold", threshold, minimum=0, maximum=1)
    _integer("min_periods", min_periods, minimum=2)
    _integer("max_columns", max_columns, minimum=1)
    _choice("overflow", overflow, {"error", "skip"})
    if top_pairs is not None:
        _integer("top_pairs", top_pairs, minimum=1)
    if sample_rows is not None:
        _integer("sample_rows", sample_rows, minimum=2)
    numeric_names = _get_context(df, _context).numeric_names
    if columns is not None:
        unknown = [name for name in columns if name not in df.columns]
        if unknown:
            raise KeyError(f"Correlation columns were not found: {unknown!r}.")
        names = [name for name in columns if name in numeric_names]
    else:
        names = numeric_names
    if len(names) > max_columns:
        if overflow == "error":
            raise ValueError(
                f"correlations supports at most {max_columns} numeric columns; "
                "use columns=, overflow='skip', or increase max_columns."
            )
        return {
            "matrix": pd.DataFrame(),
            "pairs": pd.DataFrame(columns=_CORRELATION_PAIR_COLUMNS),
        }
    clean = df[names].replace([inf, -inf], nan)
    if method == "kendall" and len(clean) > 10_000 and sample_rows is None:
        raise ValueError("kendall requires sample_rows for more than 10000 rows.")
    if sample_rows is not None and len(clean) > sample_rows:
        clean = clean.sample(n=sample_rows, random_state=random_state)
    calculated_matrix = clean.corr(method=method, min_periods=min_periods)
    rows = []
    for left_index, right_index in combinations(range(len(names)), 2):
        left, right = names[left_index], names[right_index]
        value = cast(float, calculated_matrix.iat[left_index, right_index])
        if pd.isna(value) or abs(value) < threshold:
            continue
        rows.append(
            {
                "column_1": left,
                "column_2": right,
                "correlation": value,
                "absolute_correlation": abs(value),
                "direction": (
                    "positive" if value > 0 else "negative" if value < 0 else "none"
                ),
                "strength": _strength(abs(value)),
            }
        )
    pairs = pd.DataFrame(rows, columns=_CORRELATION_PAIR_COLUMNS)
    if not pairs.empty:
        pairs = pairs.sort_values("absolute_correlation", ascending=False).reset_index(
            drop=True
        )
        if top_pairs is not None:
            pairs = pairs.head(top_pairs)
    matrix = calculated_matrix if include_matrix else pd.DataFrame()
    return {"matrix": matrix, "pairs": pairs}


@overload
def target(
    df: pd.DataFrame,
    target_column: ColumnName,
    imbalance_ratio: float = 3,
    *,
    target_type: Literal["categorical"],
    _correlation_result: CorrelationResult | None = None,
    _outlier_result: pd.DataFrame | None = None,
    _context: AnalysisContext | None = None,
) -> CategoricalTargetResult: ...


@overload
def target(
    df: pd.DataFrame,
    target_column: ColumnName,
    imbalance_ratio: float = 3,
    *,
    target_type: Literal["numeric"],
    _correlation_result: CorrelationResult | None = None,
    _outlier_result: pd.DataFrame | None = None,
    _context: AnalysisContext | None = None,
) -> NumericTargetResult: ...


@overload
def target(
    df: pd.DataFrame,
    target_column: ColumnName,
    imbalance_ratio: float = 3,
    *,
    target_type: Literal["auto"] = "auto",
    _correlation_result: CorrelationResult | None = None,
    _outlier_result: pd.DataFrame | None = None,
    _context: AnalysisContext | None = None,
) -> TargetResult: ...


@overload
def target(
    df: pd.DataFrame,
    target_column: ColumnName,
    imbalance_ratio: float = 3,
    *,
    target_type: TargetType,
    _correlation_result: CorrelationResult | None = None,
    _outlier_result: pd.DataFrame | None = None,
    _context: AnalysisContext | None = None,
) -> TargetResult: ...


def target(
    df: pd.DataFrame,
    target_column: ColumnName,
    imbalance_ratio: float = 3,
    *,
    target_type: TargetType = "auto",
    _correlation_result: CorrelationResult | None = None,
    _outlier_result: pd.DataFrame | None = None,
    _context: AnalysisContext | None = None,
) -> TargetResult:
    """Return a categorical or numeric target summary."""
    validate(df, target_column)
    _number(
        "imbalance_ratio",
        imbalance_ratio,
        minimum=1,
        include_minimum=False,
    )
    _choice("target_type", target_type, {"auto", "categorical", "numeric"})
    context = _get_context(df, _context)
    series = df[target_column]
    clean = series.dropna()
    categorical_target = target_type == "categorical" or (
        target_type == "auto"
        and (
            context.columns[target_column].kind in {"categorical", "boolean"}
            or context.columns[target_column].unique <= 20
        )
    )
    if categorical_target:
        counts = context.columns[target_column].value_counts
        distribution = counts.rename("count").to_frame()
        distribution["percentage"] = [
            _pct(int(value), len(clean)) for value in counts.to_numpy()
        ]
        distribution = distribution.rename_axis("value").reset_index()
        ratio = float(counts.max() / counts.min()) if len(counts) > 1 else 1.0
        return {
            "type": "categorical",
            "classes": len(counts),
            "missing": int(series.isna().sum()),
            "majority_class": counts.index[0] if not counts.empty else None,
            "minority_class": counts.index[-1] if not counts.empty else None,
            "majority_to_minority_ratio": round(ratio, 2),
            "imbalanced": ratio >= imbalance_ratio,
            "distribution": distribution,
        }
    correlation_result = _correlation_result or correlations(df, threshold=0)
    related = correlation_result["pairs"]
    related = related[
        related["column_1"].eq(cast(Any, target_column))
        | related["column_2"].eq(cast(Any, target_column))
    ].reset_index(drop=True)
    outlier_result = (
        _outlier_result
        if _outlier_result is not None
        else outliers(df[[target_column]])
    )
    return {
        "type": "numeric",
        "missing": int(series.isna().sum()),
        "summary": numeric(df[[target_column]]),
        "outliers": outlier_result.loc[
            outlier_result["column"].eq(cast(Any, target_column))
        ].reset_index(drop=True),
        "correlations": related,
    }
