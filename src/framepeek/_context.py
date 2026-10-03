"""Internal per-run metadata reused by profile analyses."""

from dataclasses import dataclass, field
from functools import cached_property

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

from ._values import DuplicateData, ValueCount, duplicate_data, value_counts
from .types import ColumnName
from .validation import validate


def column_kind(series: pd.Series) -> str:
    if is_bool_dtype(series.dtype):
        return "boolean"
    if is_numeric_dtype(series.dtype):
        return "numeric"
    if is_datetime64_any_dtype(series.dtype):
        return "datetime"
    if (
        isinstance(series.dtype, (pd.CategoricalDtype, pd.StringDtype))
        or series.dtype == object
    ):
        return "categorical"
    return "other"


@dataclass(frozen=True)
class ColumnMetadata:
    series: pd.Series
    kind: str
    non_null: int
    missing: int

    @cached_property
    def value_counts(self) -> tuple[ValueCount, ...]:
        return value_counts(self.series)

    @cached_property
    def unique(self) -> int:
        if self.series.dtype == object or isinstance(
            self.series.dtype, pd.CategoricalDtype
        ):
            return len(self.value_counts)
        return int(self.series.nunique())

    @cached_property
    def top(self) -> ValueCount | None:
        if self.kind == "categorical" or self.series.dtype == object:
            counts = self.value_counts
            return counts[0] if counts else None
        # Keep only the leading value, not one Python object per distinct number.
        native_counts = self.series.dropna().value_counts()
        if native_counts.empty:
            return None
        value, count = next(iter(native_counts.items()))
        return ValueCount(value, int(count), False)


@dataclass(frozen=True)
class AnalysisContext:
    frame: pd.DataFrame
    columns: dict[ColumnName, ColumnMetadata]
    warning_samples: dict[ColumnName, tuple[int, bool]] = field(default_factory=dict)

    @classmethod
    def from_frame(cls, df: pd.DataFrame) -> "AnalysisContext":
        validate(df)
        metadata: dict[ColumnName, ColumnMetadata] = {}
        for name in df.columns:
            series = df[name]
            non_null = int(series.notna().sum())
            metadata[name] = ColumnMetadata(
                series=series,
                kind=column_kind(series),
                non_null=non_null,
                missing=len(series) - non_null,
            )
        return cls(df, metadata)

    @cached_property
    def duplicates(self) -> DuplicateData:
        return duplicate_data(self.frame)

    @property
    def numeric_names(self) -> list[ColumnName]:
        return [
            name
            for name, metadata in self.columns.items()
            if metadata.kind == "numeric"
        ]
