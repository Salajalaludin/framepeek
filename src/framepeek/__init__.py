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
from .report import format_report, print_report, profile
from .serialization import to_serializable
from .types import (
    CategoricalTargetResult,
    ColumnName,
    CorrelationMethod,
    CorrelationOverflow,
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
from .warnings import quality_warnings, warnings

__version__ = version("framepeek")

__all__ = [
    "__version__",
    "ColumnName",
    "CategoricalTargetResult",
    "CorrelationMethod",
    "CorrelationOverflow",
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
    "format_report",
    "missing",
    "numeric",
    "outliers",
    "overview",
    "print_report",
    "profile",
    "quality_warnings",
    "target",
    "to_serializable",
    "validate",
    "warnings",
]
