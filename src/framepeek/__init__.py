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
    ColumnName,
    CorrelationMethod,
    OutlierMethod,
    Severity,
)
from .validation import validate
from .warnings import warnings

__version__ = version("framepeek")

__all__ = [
    "__version__",
    "ColumnName",
    "CorrelationMethod",
    "OutlierMethod",
    "Severity",
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
