"""Safe internal identity and grouping for arbitrary DataFrame values."""

from dataclasses import dataclass
from typing import Any, Hashable, cast

import numpy as np
import pandas as pd

from .types import ColumnName


@dataclass(frozen=True)
class _ValueKey:
    kind: str
    value_type: type[object]
    value: Hashable


@dataclass(frozen=True, eq=False)
class _EqualityKey:
    value: object

    def __hash__(self) -> int:
        # ponytail: constant per type; specialize if opaque-object cardinality
        # becomes a measured bottleneck.
        return hash(type(self.value))

    def __eq__(self, other: object) -> bool:
        other_value = cast(_EqualityKey, other).value
        if self.value is other_value:
            return True
        try:
            result = self.value == other_value
            return not hasattr(result, "__len__") and bool(result)
        except Exception:
            return False


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
    if isinstance(value, (list, dict, set, frozenset, tuple, np.ndarray)):
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
        elif isinstance(value, np.ndarray):
            nested = (
                value.shape,
                str(value.dtype),
                tuple(_identity(item, active)[0] for item in value.flat),
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
        return _ValueKey(
            "equality", type(value), _EqualityKey(value)
        ), True
    return _ValueKey("scalar", type(value), value), False


def _can_use_pandas_counts(values: pd.Series) -> bool:
    value_type: type[object] | None = None
    try:
        for value in values:
            if value_type is None:
                value_type = type(value)
            elif type(value) is not value_type:
                return False
            hash(value)
    except Exception:
        return False
    return True


def value_counts(series: pd.Series) -> tuple[ValueCount, ...]:
    """Count values without requiring them to be hashable."""
    clean = series[series.notna()]
    use_fast_path = series.dtype != object or (
        _can_use_pandas_counts(clean)
    )
    if use_fast_path:
        try:
            counts = clean.value_counts()
        except Exception:
            pass
        else:
            return tuple(
                ValueCount(value, int(count), False)
                for value, count in counts.items()
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


def _can_use_pandas_duplicates(
    df: pd.DataFrame,
    columns: list[ColumnName],
) -> bool:
    for name in columns:
        series = df[name]
        if series.dtype != object:
            continue
        if bool(series.isna().any()):
            return False
        value_type: type[object] | None = None
        try:
            for value in series:
                if isinstance(
                    value,
                    (list, dict, set, frozenset, tuple, np.ndarray),
                ):
                    return False
                if value_type is None:
                    value_type = type(value)
                elif type(value) is not value_type:
                    return False
                hash(value)
        except Exception:
            return False
    return True


def _pandas_duplicate_data(
    df: pd.DataFrame,
    columns: list[ColumnName],
) -> DuplicateData:
    selected = df.loc[:, columns]
    repeated_mask = selected.duplicated(keep=False)
    repeated = selected.loc[repeated_mask]
    if repeated.empty:
        return DuplicateData(
            pd.Series(False, index=df.index, dtype=bool),
            repeated_mask,
            pd.DataFrame(columns=[*columns, "count"]),
        )

    codes, _ = pd.factorize(
        pd.MultiIndex.from_frame(repeated),
        sort=False,
        use_na_sentinel=False,
    )
    group_counts = np.bincount(codes)
    _, first_positions = np.unique(codes, return_index=True)
    repeated_positions = np.flatnonzero(repeated_mask.to_numpy())

    duplicate_mask = repeated_mask.copy()
    duplicate_mask.iloc[repeated_positions[first_positions]] = False

    order = np.argsort(-group_counts, kind="stable")
    representatives = repeated.iloc[first_positions[order]].reset_index(
        drop=True
    )
    groups = pd.concat(
        [
            representatives,
            pd.Series(group_counts[order], name="count"),
        ],
        axis=1,
    )
    return DuplicateData(duplicate_mask, repeated_mask, groups)


def duplicate_mask(df: pd.DataFrame) -> pd.Series:
    """Return a first-occurrence duplicate mask without building groups."""
    columns: list[ColumnName] = list(df.columns)
    if _can_use_pandas_duplicates(df, columns):
        try:
            return df.duplicated()
        except Exception:
            pass
    duplicate_mask, _ = _duplicate_masks(_row_keys(df, columns), df.index)
    return duplicate_mask


def _structural_duplicate_data(
    df: pd.DataFrame,
    columns: list[ColumnName],
) -> DuplicateData:
    keys = _row_keys(df, columns)
    duplicate_mask, repeated_mask = _duplicate_masks(keys, df.index)
    grouped: dict[
        tuple[_ValueKey, ...], tuple[tuple[object, ...], int]
    ] = {}
    rows = df.loc[:, columns].itertuples(index=False, name=None)
    for key, row, is_repeated in zip(keys, rows, repeated_mask):
        if not is_repeated:
            continue
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


def duplicate_data(
    df: pd.DataFrame,
    subset: list[ColumnName] | None = None,
) -> DuplicateData:
    """Return duplicate masks and groups without hash-dependent pandas calls."""
    columns: list[ColumnName] = (
        subset if subset is not None else list(df.columns)
    )
    if _can_use_pandas_duplicates(df, columns):
        try:
            return _pandas_duplicate_data(df, columns)
        except Exception:
            pass
    return _structural_duplicate_data(df, columns)
