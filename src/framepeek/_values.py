"""Safe internal identity and grouping for arbitrary DataFrame values."""

from dataclasses import dataclass
from typing import Any, Hashable, Literal, cast

import pandas as pd

from .types import ColumnName


@dataclass(frozen=True)
class _ValueKey:
    kind: str
    value_type: type[object]
    value: Hashable


@dataclass(frozen=True)
class ValueCount:
    value: object
    count: int
    transformed: bool


@dataclass(frozen=True)
class DuplicateData:
    duplicate_mask: pd.Series
    repeated_mask: pd.Series
    groups: pd.DataFrame


def _identity(
    value: object,
    active: set[int] | None = None,
) -> tuple[_ValueKey, bool]:
    active = active or set()
    value_id = id(value)
    if isinstance(value, (list, dict, set, frozenset, tuple)):
        if value_id in active:
            return _ValueKey("identity", type(value), value_id), True
        active.add(value_id)
        nested: Hashable
        if isinstance(value, list):
            nested = tuple(_identity(item, active)[0] for item in value)
        elif isinstance(value, tuple):
            nested = tuple(_identity(item, active)[0] for item in value)
        elif isinstance(value, dict):
            nested = frozenset(
                (_identity(key, active)[0], _identity(item, active)[0])
                for key, item in value.items()
            )
        else:
            nested = frozenset(_identity(item, active)[0] for item in value)
        active.remove(value_id)
        return _ValueKey("structural", type(value), nested), True

    missing = pd.isna(cast(Any, value))
    if not hasattr(missing, "__len__") and bool(missing):
        return _ValueKey("missing", type(value), ""), False
    try:
        hash(value)
    except Exception:
        return _ValueKey("identity", type(value), value_id), True
    return _ValueKey("scalar", type(value), value), False


def value_counts(series: pd.Series) -> tuple[ValueCount, ...]:
    """Count values without requiring them to be hashable."""
    clean = series[series.notna()]
    types: list[type[object]] = (
        clean.map(type).unique().tolist() if series.dtype == object else []
    )
    if series.dtype != object or (
        len(types) == 1 and types[0].__hash__ is not None
    ):
        return tuple(
            ValueCount(value, int(count), False)
            for value, count in clean.value_counts().items()
        )
    groups: dict[_ValueKey, ValueCount] = {}
    for value in clean:
        key, transformed = _identity(value)
        if key in groups:
            item = groups[key]
            groups[key] = ValueCount(item.value, item.count + 1, transformed)
        else:
            groups[key] = ValueCount(value, 1, transformed)
    return tuple(
        sorted(groups.values(), key=lambda item: item.count, reverse=True)
    )


def _row_keys(
    df: pd.DataFrame,
    columns: list[ColumnName],
) -> list[tuple[_ValueKey, ...]]:
    return [
        tuple(_identity(value)[0] for value in row)
        for row in df.loc[:, columns].itertuples(index=False, name=None)
    ]


def _duplicate_masks(
    keys: list[tuple[_ValueKey, ...]],
    index: pd.Index,
) -> tuple[pd.Series, pd.Series]:
    counts: dict[tuple[_ValueKey, ...], int] = {}
    for key in keys:
        counts[key] = counts.get(key, 0) + 1
    seen: set[tuple[_ValueKey, ...]] = set()
    duplicate_mask = []
    repeated_mask = []
    for key in keys:
        duplicate_mask.append(key in seen)
        repeated_mask.append(counts[key] > 1)
        seen.add(key)
    return (
        pd.Series(duplicate_mask, index=index, dtype=bool),
        pd.Series(repeated_mask, index=index, dtype=bool),
    )


def duplicated(
    df: pd.DataFrame,
    subset: list[ColumnName] | None = None,
    *,
    keep: Literal["first", False] = "first",
) -> pd.Series:
    """Return a pandas-compatible duplicate mask for arbitrary values."""
    columns: list[ColumnName] = (
        subset if subset is not None else list(df.columns)
    )
    duplicate_mask, repeated_mask = _duplicate_masks(
        _row_keys(df, columns), df.index
    )
    return repeated_mask if keep is False else duplicate_mask


def duplicate_data(
    df: pd.DataFrame,
    subset: list[ColumnName] | None = None,
) -> DuplicateData:
    """Return duplicate masks and groups without hash-dependent pandas calls."""
    columns: list[ColumnName] = (
        subset if subset is not None else list(df.columns)
    )
    duplicate_mask, repeated_mask = _duplicate_masks(
        _row_keys(df, columns), df.index
    )
    repeated = df.loc[repeated_mask, columns]
    grouped: dict[
        tuple[_ValueKey, ...], tuple[tuple[object, ...], int]
    ] = {}
    for row in repeated.itertuples(index=False, name=None):
        key = tuple(_identity(value)[0] for value in row)
        if key in grouped:
            values, count = grouped[key]
            grouped[key] = values, count + 1
        else:
            grouped[key] = row, 1
    groups = pd.DataFrame(
        [
            [*values, count]
            for values, count in sorted(
                grouped.values(), key=lambda group: group[1], reverse=True
            )
        ],
        columns=[*columns, "count"],
    )
    return DuplicateData(duplicate_mask, repeated_mask, groups)
