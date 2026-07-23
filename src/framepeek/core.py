"""Functional API for FramePeek's first usable release."""

from __future__ import annotations

from collections.abc import Hashable, Sequence
from itertools import combinations
from math import inf, nan
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)


def validate(df: pd.DataFrame, target: Hashable | None = None) -> None:
    """Validate the common DataFrame and target requirements."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas.DataFrame, received {type(df).__name__}.")
    if df.empty or len(df.columns) == 0:
        raise ValueError("DataFrame must contain at least one row and one column.")
    if df.columns.has_duplicates:
        raise ValueError("DataFrame column names must be unique.")
    if target is not None and target not in df.columns:
        raise KeyError(f"Target column {target!r} was not found.")


def _pct(value: int | float, total: int) -> float:
    return round(float(value) / total * 100, 2) if total else 0.0


def _kind(series: pd.Series) -> str:
    if is_bool_dtype(series.dtype):
        return "boolean"
    if is_numeric_dtype(series.dtype):
        return "numeric"
    if is_datetime64_any_dtype(series.dtype):
        return "datetime"
    if isinstance(series.dtype, pd.CategoricalDtype) or series.dtype == object:
        return "categorical"
    if isinstance(series.dtype, pd.StringDtype):
        return "categorical"
    return "other"


def _numeric_names(df: pd.DataFrame) -> list[Hashable]:
    return [
        name
        for name in df.columns
        if is_numeric_dtype(df[name].dtype) and not is_bool_dtype(df[name].dtype)
    ]


def overview(df: pd.DataFrame) -> pd.DataFrame:
    """Return dataset-level size, quality, memory, and type metrics."""
    validate(df)
    rows, column_count = df.shape
    total_cells = rows * column_count
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    kinds = pd.Series([_kind(df[name]) for name in df.columns]).value_counts()
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


def columns(df: pd.DataFrame, high_cardinality_ratio: float = 0.5) -> pd.DataFrame:
    """Return one structural and quality summary row per column."""
    validate(df)
    if not 0 < high_cardinality_ratio <= 1:
        raise ValueError("high_cardinality_ratio must be in (0, 1].")

    rows: list[dict[str, Any]] = []
    for name in df.columns:
        series = df[name]
        non_null = int(series.notna().sum())
        unique = int(series.nunique(dropna=True))
        counts = series.value_counts(dropna=True)
        top = counts.index[0] if not counts.empty else None
        top_frequency = int(counts.iloc[0]) if not counts.empty else 0
        kind = _kind(series)
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
) -> pd.DataFrame:
    """Return per-column missingness; row-level totals live in ``result.attrs``."""
    validate(df)
    if not isinstance(thresholds, tuple) or len(thresholds) != 3:
        raise ValueError("thresholds must contain exactly three values.")
    low, moderate, high = thresholds
    if not 0 <= low < moderate < high <= 100:
        raise ValueError("thresholds must be three increasing values within 0..100.")

    counts = df.isna().sum()
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
    result.attrs["rows"] = {
        "rows_with_missing": incomplete,
        "complete_rows": len(df) - incomplete,
        "complete_rows_pct": _pct(len(df) - incomplete, len(df)),
    }
    return result.sort_values("missing", ascending=False, kind="stable").reset_index(
        drop=True
    )


def duplicates(
    df: pd.DataFrame,
    subset: Sequence[Hashable] | None = None,
    max_examples: int = 5,
) -> dict[str, Any]:
    """Return duplicate totals, repeated groups, and bounded examples."""
    validate(df)
    if not isinstance(max_examples, int) or max_examples < 0:
        raise ValueError("max_examples must be non-negative.")
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


def numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric, non-boolean columns."""
    validate(df)
    rows: list[dict[str, Any]] = []
    for name in _numeric_names(df):
        clean = df[name].replace([inf, -inf], nan).dropna()
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
                "missing": len(df) - count,
                "missing_pct": _pct(len(df) - count, len(df)),
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
) -> pd.DataFrame:
    """Return frequency and cardinality summaries for categorical columns."""
    validate(df)
    if (
        not isinstance(top_n, int)
        or not isinstance(rare_max_count, int)
        or top_n <= 0
        or rare_max_count < 1
    ):
        raise ValueError("top_n and rare_max_count must be positive integers.")
    rows: list[dict[str, Any]] = []
    for name in df.columns:
        series = df[name]
        if _kind(series) not in {"categorical", "boolean"}:
            continue
        counts = series.value_counts(dropna=True)
        non_null = int(series.notna().sum())
        unique = len(counts)
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
]


def outliers(
    df: pd.DataFrame,
    method: str = "iqr",
    multiplier: float = 1.5,
) -> pd.DataFrame:
    """Return IQR-based potential outlier summaries for numeric columns."""
    validate(df)
    if method != "iqr":
        raise ValueError("method must be 'iqr'.")
    if multiplier <= 0:
        raise ValueError("multiplier must be greater than zero.")
    rows: list[dict[str, Any]] = []
    for name in _numeric_names(df):
        clean = df[name].replace([inf, -inf], nan).dropna()
        if clean.empty:
            rows.append({"column": name})
            continue
        q1, q3 = clean.quantile([0.25, 0.75])
        iqr = q3 - q1
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


def correlations(
    df: pd.DataFrame,
    method: str = "pearson",
    threshold: float = 0,
) -> dict[str, pd.DataFrame]:
    """Return a numeric correlation matrix and a tidy pair table."""
    validate(df)
    if method not in {"pearson", "spearman", "kendall"}:
        raise ValueError("method must be 'pearson', 'spearman', or 'kendall'.")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be within 0..1.")
    names = _numeric_names(df)
    clean = df[names].replace([inf, -inf], nan)
    matrix = clean.corr(method=method)
    rows = []
    for left, right in combinations(names, 2):
        value = matrix.loc[left, right]
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
    pair_columns = [
        "column_1",
        "column_2",
        "correlation",
        "absolute_correlation",
        "direction",
        "strength",
    ]
    pairs = pd.DataFrame(rows, columns=pair_columns)
    if not pairs.empty:
        pairs = pairs.sort_values("absolute_correlation", ascending=False).reset_index(
            drop=True
        )
    return {"matrix": matrix, "pairs": pairs}


def target(
    df: pd.DataFrame,
    target: Hashable,
    imbalance_ratio: float = 3,
) -> dict[str, Any]:
    """Return a categorical or numeric target summary."""
    validate(df, target)
    if imbalance_ratio <= 1:
        raise ValueError("imbalance_ratio must be greater than one.")
    series = df[target]
    clean = series.dropna()
    categorical_target = _kind(series) in {"categorical", "boolean"} or (
        clean.nunique() <= 20
    )
    if categorical_target:
        counts = clean.value_counts(dropna=True)
        distribution = counts.rename("count").to_frame()
        distribution["percentage"] = [
            _pct(value, len(clean)) for value in counts.to_numpy()
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
    related = correlations(df, threshold=0)["pairs"]
    related = related[
        related["column_1"].eq(target) | related["column_2"].eq(target)
    ].reset_index(drop=True)
    return {
        "type": "numeric",
        "missing": int(series.isna().sum()),
        "summary": numeric(df[[target]]),
        "outliers": outliers(df[[target]]),
        "correlations": related,
    }


_target_summary = target


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
    target: Hashable | None = None,
    missing_threshold: float = 20,
    near_constant_ratio: float = 0.95,
    high_cardinality_ratio: float = 0.5,
    outlier_threshold: float = 5,
    imbalance_ratio: float = 3,
) -> pd.DataFrame:
    """Return actionable data-quality warnings."""
    validate(df, target)
    if not 0 <= missing_threshold <= 100 or not 0 < outlier_threshold <= 100:
        raise ValueError("percentage thresholds must be within 0..100.")
    if not 0 < near_constant_ratio <= 1:
        raise ValueError("near_constant_ratio must be in (0, 1].")
    if not 0 < high_cardinality_ratio <= 1:
        raise ValueError("high_cardinality_ratio must be in (0, 1].")

    rows: list[dict[str, Any]] = []

    def add(
        code: str,
        severity: str,
        column: Hashable | None,
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
        non_null = series.dropna()
        unique = int(non_null.nunique())
        missing_pct = _pct(series.isna().sum(), len(series))
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
            top_ratio = float(non_null.value_counts().iloc[0] / len(non_null))
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
        if _kind(series) == "categorical" and unique > 20 and ratio >= high_cardinality_ratio:
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
        if _kind(series) == "categorical":
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

    for row in outliers(df).itertuples(index=False):
        if pd.notna(row.outlier_pct) and row.outlier_pct > outlier_threshold:
            add(
                "potential_outliers",
                "medium",
                row.column,
                f"Column {row.column!r} contains {row.outlier_pct}% potential outliers.",
                "Review them in domain context; do not remove automatically.",
                row.outlier_pct,
            )

    if target is not None:
        target_result = _target_summary(df, target, imbalance_ratio)
        if target_result["type"] == "categorical" and target_result["imbalanced"]:
            ratio = target_result["majority_to_minority_ratio"]
            add(
                "class_imbalance",
                "high",
                target,
                f"Target {target!r} has a majority-to-minority ratio of {ratio}.",
                "Use stratified evaluation and imbalance-aware metrics.",
                ratio,
            )
    return pd.DataFrame(rows, columns=_WARNING_COLUMNS)


def profile(
    df: pd.DataFrame,
    target: Hashable | None = None,
    correlation_method: str = "pearson",
    outlier_method: str = "iqr",
    outlier_multiplier: float = 1.5,
    top_n_categories: int = 5,
    missing_thresholds: tuple[float, float, float] = (5, 20, 50),
    warning_missing_threshold: float = 20,
    high_cardinality_ratio: float = 0.5,
    imbalance_ratio: float = 3,
) -> dict[str, Any]:
    """Run every MVP analysis without mutating the input DataFrame."""
    validate(df, target)
    return {
        "overview": overview(df),
        "columns": columns(df, high_cardinality_ratio),
        "missing": missing(df, missing_thresholds),
        "duplicates": duplicates(df),
        "numeric": numeric(df),
        "categorical": categorical(df, top_n_categories),
        "outliers": outliers(df, outlier_method, outlier_multiplier),
        "correlations": correlations(df, correlation_method),
        "target": _target_summary(df, target, imbalance_ratio)
        if target is not None
        else None,
        "warnings": warnings(
            df,
            target=target,
            missing_threshold=warning_missing_threshold,
            high_cardinality_ratio=high_cardinality_ratio,
            imbalance_ratio=imbalance_ratio,
        ),
    }
