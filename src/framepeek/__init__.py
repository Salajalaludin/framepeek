"""Lightweight exploratory data analysis for pandas DataFrames."""

from importlib.metadata import version

from .analysis import (
    categorical,
    columns,
    correlations,
    duplicates,
    missing,
    numeric,
    outliers,
    overview,
    target,
)
from .report import print_report, profile
from .types import (
    CategoricalTargetResult,
    ColumnName,
    CorrelationMethod,
    CorrelationResult,
    DuplicatesResult,
    NumericTargetResult,
    OutlierMethod,
    ProfileResult,
    Severity,
    TargetResult,
    TargetType,
    WarningsResult,
)
from .validation import validate
from .warnings import warnings

__version__ = version("framepeek")

__all__ = [
    "__version__",
    "ColumnName",
    "CategoricalTargetResult",
    "CorrelationMethod",
    "CorrelationResult",
    "DuplicatesResult",
    "NumericTargetResult",
    "OutlierMethod",
    "ProfileResult",
    "Severity",
    "TargetResult",
    "TargetType",
    "WarningsResult",
    "categorical",
    "columns",
    "correlations",
    "duplicates",
    "missing",
    "numeric",
    "outliers",
    "overview",
    "print_report",
    "profile",
    "target",
    "validate",
    "warnings",
]
