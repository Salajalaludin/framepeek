"""Public configuration and result types."""

from collections.abc import Hashable
from typing import Literal, TypedDict

import pandas as pd

ColumnName = Hashable
CorrelationMethod = Literal["pearson", "spearman", "kendall"]
CorrelationOverflow = Literal["error", "skip"]
OutlierMethod = Literal["iqr"]
Severity = Literal["critical", "high", "medium", "low"]
TargetType = Literal["auto", "categorical", "numeric"]


class CorrelationResult(TypedDict):
    matrix: pd.DataFrame
    pairs: pd.DataFrame


class DuplicatesResult(TypedDict):
    duplicate_rows: int
    duplicate_pct: float
    duplicate_groups: int
    unique_rows: int
    groups: pd.DataFrame
    examples: pd.DataFrame


class MissingRowsResult(TypedDict):
    rows_with_missing: int
    complete_rows: int
    complete_rows_pct: float


class MissingResult(TypedDict):
    columns: pd.DataFrame
    rows: MissingRowsResult
    patterns: pd.DataFrame


class CategoricalTargetResult(TypedDict):
    type: Literal["categorical"]
    classes: int
    missing: int
    majority_class: object
    minority_class: object
    majority_to_minority_ratio: float
    imbalanced: bool
    distribution: pd.DataFrame


class NumericTargetResult(TypedDict):
    type: Literal["numeric"]
    missing: int
    summary: pd.DataFrame
    outliers: pd.DataFrame
    correlations: pd.DataFrame


TargetResult = CategoricalTargetResult | NumericTargetResult
WarningsResult = pd.DataFrame


class ProfileResult(TypedDict):
    metadata: dict[str, object]
    overview: pd.DataFrame
    columns: pd.DataFrame
    missing: MissingResult
    duplicates: DuplicatesResult
    numeric: pd.DataFrame
    categorical: pd.DataFrame
    outliers: pd.DataFrame
    correlations: CorrelationResult
    target: TargetResult | None
    warnings: WarningsResult
