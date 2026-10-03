"""Run with an installed distribution, outside the source tree."""

import json
import sys
from importlib.metadata import version

import pandas as pd

import framepeek as fp


def main() -> None:
    expected = sys.argv[1]
    assert fp.__version__ == version("framepeek") == expected
    frame = pd.DataFrame(
        {"x": [1.0, 2.0, 3.0, 100.0, None], "text": ["a", "a", "b", "b", None]}
    )
    report = fp.profile(frame, target_column="text", warning_sample_size=2)
    assert set(report) == {
        "metadata",
        "overview",
        "columns",
        "missing",
        "duplicates",
        "numeric",
        "categorical",
        "outliers",
        "correlations",
        "target",
        "warnings",
    }
    assert report["metadata"]["schema_version"] == "1.1"
    assert report["metadata"]["framepeek_version"] == expected
    assert report["metadata"]["sampling"] == {
        "warnings_used": True,
        "warning_sample_size": 2,
        "random_state": 0,
    }
    assert list(report["columns"].column) == ["x", "text"]
    assert report["numeric"].iloc[0]["count"] == 4
    assert report["missing"]["rows"] == {
        "rows_with_missing": 1,
        "complete_rows": 4,
        "complete_rows_pct": 80.0,
    }
    assert report["missing"]["patterns"].iloc[0].missing_columns == ("x", "text")
    assert set(report["duplicates"]) == {
        "duplicate_rows",
        "duplicate_pct",
        "duplicate_groups",
        "unique_rows",
        "groups",
        "examples",
    }
    assert set(report["correlations"]) == {"matrix", "pairs"}
    assert report["target"]["type"] == "categorical"
    assert list(report["target"]["distribution"].columns) == [
        "value",
        "count",
        "percentage",
        "transformed",
    ]
    assert list(report["warnings"].columns) == [
        "code",
        "severity",
        "column",
        "message",
        "recommendation",
        "metric",
    ]
    encoded = fp.to_serializable(report)
    assert encoded["schema_version"] == "1.0" and encoded["exact"] is True
    assert encoded["data"]["columns"]["type"] == "dataframe"
    assert encoded["data"]["columns"]["columns"] == list(report["columns"].columns)
    json.dumps(encoded, allow_nan=False)
    print(f"Installed FramePeek {expected}: report and serialization schemas verified")


if __name__ == "__main__":
    main()
