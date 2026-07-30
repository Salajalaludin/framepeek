"""Internal per-run metadata reused by profile analyses."""

from dataclasses import dataclass

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

from ._values import ValueCount, value_counts
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
    kind: str
    non_null: int
    missing: int
    unique: int
    value_counts: tuple[ValueCount, ...]


@dataclass(frozen=True)
class AnalysisContext:
    columns: dict[ColumnName, ColumnMetadata]

    @classmethod
    def from_frame(cls, df: pd.DataFrame) -> "AnalysisContext":
        validate(df)
        metadata: dict[ColumnName, ColumnMetadata] = {}
        for name in df.columns:
            series = df[name]
            counts = value_counts(series)
            non_null = int(series.notna().sum())
            metadata[name] = ColumnMetadata(
                kind=column_kind(series),
                non_null=non_null,
                missing=len(series) - non_null,
                unique=len(counts),
                value_counts=counts,
            )
        return cls(metadata)

    @property
    def numeric_names(self) -> list[ColumnName]:
        return [
            name
            for name, metadata in self.columns.items()
            if metadata.kind == "numeric"
        ]
