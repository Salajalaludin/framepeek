"""Public configuration and result types."""

from collections.abc import Hashable
from typing import Literal, TypedDict

import pandas as pd

ColumnName = Hashable
CorrelationMethod = Literal["pearson", "spearman", "kendall"]
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
    overview: pd.DataFrame
    columns: pd.DataFrame
    missing: pd.DataFrame
    duplicates: DuplicatesResult
    numeric: pd.DataFrame
    categorical: pd.DataFrame
    outliers: pd.DataFrame
    correlations: CorrelationResult
    target: TargetResult | None
    warnings: WarningsResult
