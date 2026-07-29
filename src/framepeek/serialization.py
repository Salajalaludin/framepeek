"""Machine-readable conversion for FramePeek results."""

from datetime import date, datetime
from math import isinf, isnan
from typing import Any

import pandas as pd


def to_serializable(value: Any) -> Any:
    """Convert report values to JSON-compatible Python objects."""
    if isinstance(value, pd.DataFrame):
        return [to_serializable(row) for row in value.to_dict(orient="records")]
    if isinstance(value, dict):
        return {str(key): to_serializable(nested) for key, nested in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if value is pd.NA or value is pd.NaT:
        return None
    if hasattr(value, "item"):
        return to_serializable(value.item())
    if isinstance(value, float):
        if isnan(value):
            return None
        if isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
