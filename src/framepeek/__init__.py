"""Lightweight exploratory data analysis for pandas DataFrames."""

from importlib.metadata import version

from .core import (
    categorical,
    columns,
    correlations,
    duplicates,
    missing,
    numeric,
    outliers,
    overview,
    print_report,
    profile,
    target,
    validate,
    warnings,
)

__version__ = version("framepeek")

__all__ = [
    "__version__",
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
