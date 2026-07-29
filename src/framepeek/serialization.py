"""Machine-readable conversion for FramePeek results."""

from datetime import date, datetime
from math import isinf, isnan
from typing import Any

import pandas as pd

SERIALIZATION_SCHEMA_VERSION = "1.0"


def _convert(value: Any) -> tuple[Any, bool]:
    if isinstance(value, pd.DataFrame):
        index, index_exact = _convert(list(value.index))
        index_names, index_names_exact = _convert(list(value.index.names))
        columns, columns_exact = _convert(list(value.columns))
        data, data_exact = _convert(
            list(value.itertuples(index=False, name=None))
        )
        return (
            {
                "type": "dataframe",
                "index": index,
                "index_names": index_names,
                "columns": columns,
                "data": data,
            },
            index_exact
            and index_names_exact
            and columns_exact
            and data_exact,
        )
    if isinstance(value, dict):
        if all(isinstance(key, str) for key in value):
            converted = [_convert(nested) for nested in value.values()]
            return (
                {
                    key: nested
                    for key, (nested, _) in zip(value, converted, strict=True)
                },
                all(exact for _, exact in converted),
            )
        entries = []
        exact = True
        for key, nested in value.items():
            converted_key, key_exact = _convert(key)
            converted_value, value_exact = _convert(nested)
            entries.append(
                {"key": converted_key, "value": converted_value}
            )
            exact = exact and key_exact and value_exact
        return {"type": "mapping", "entries": entries}, exact
    if isinstance(value, list):
        converted = [_convert(item) for item in value]
        return [item for item, _ in converted], all(
            exact for _, exact in converted
        )
    if isinstance(value, tuple):
        converted = [_convert(item) for item in value]
        return (
            {"type": "tuple", "items": [item for item, _ in converted]},
            all(exact for _, exact in converted),
        )
    if isinstance(value, (set, frozenset)):
        converted = [_convert(item) for item in value]
        return (
            {
                "type": type(value).__name__,
                "items": [item for item, _ in converted],
            },
            all(exact for _, exact in converted),
        )
    if value is pd.NA or value is pd.NaT:
        return {"type": type(value).__name__}, True
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return (
            {"type": type(value).__name__, "value": value.isoformat()},
            True,
        )
    if hasattr(value, "item"):
        converted, exact = _convert(value.item())
        return (
            {"type": type(value).__name__, "value": converted},
            exact,
        )
    if isinstance(value, float):
        if isnan(value):
            return {"type": "float", "value": "nan"}, True
        if isinf(value):
            return {
                "type": "float",
                "value": "infinity" if value > 0 else "-infinity",
            }, True
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value, True
    return (
        {
            "type": "python_object",
            "python_type": (
                f"{type(value).__module__}.{type(value).__qualname__}"
            ),
            "display": repr(value),
        },
        False,
    )


def to_serializable(value: Any) -> dict[str, Any]:
    """Convert a value to the versioned FramePeek JSON-compatible schema."""
    data, exact = _convert(value)
    return {
        "schema_version": SERIALIZATION_SCHEMA_VERSION,
        "exact": exact,
        "data": data,
    }
