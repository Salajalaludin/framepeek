"""Public type aliases for FramePeek configuration."""

from collections.abc import Hashable
from typing import Literal

ColumnName = Hashable
CorrelationMethod = Literal["pearson", "spearman", "kendall"]
OutlierMethod = Literal["iqr"]
Severity = Literal["critical", "high", "medium", "low"]
