"""Shared input and configuration validation."""

from collections import Counter
from math import isfinite
from numbers import Real

import pandas as pd

from .types import ColumnName


def _number(
    name: str,
    value: object,
    *,
    minimum: float,
    maximum: float | None = None,
    include_minimum: bool = True,
) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a finite number.")
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be a finite number.")
    below = result < minimum if include_minimum else result <= minimum
    if below or maximum is not None and result > maximum:
        lower = "[" if include_minimum else "("
        upper = str(maximum) if maximum is not None else "infinity"
        raise ValueError(f"{name} must be within {lower}{minimum}, {upper}].")
    return result


def _integer(name: str, value: object, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer.")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")
    return value


def _choice(name: str, value: object, choices: set[str]) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")
    if value not in choices:
        expected = ", ".join(repr(choice) for choice in sorted(choices))
        raise ValueError(f"{name} must be one of: {expected}.")
    return value


def validate(
    df: pd.DataFrame,
    target_column: ColumnName | None = None,
) -> None:
    """Validate the common DataFrame and target requirements."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas.DataFrame, received {type(df).__name__}.")
    if df.empty or len(df.columns) == 0:
        raise ValueError("DataFrame must contain at least one row and one column.")
    if isinstance(df.columns, pd.MultiIndex):
        raise TypeError("DataFrame columns must use a single-level Index.")
    if df.columns.has_duplicates:
        counts = Counter(df.columns)
        details = ", ".join(
            f"{name!r} ({count} occurrences)"
            for name, count in counts.items()
            if count > 1
        )
        raise ValueError(f"DataFrame columns must be unique; duplicates: {details}.")
    if target_column is not None and target_column not in df.columns:
        raise KeyError(f"Target column {target_column!r} was not found.")
