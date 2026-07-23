import pandas as pd
import pytest

import framepeek as fp
from framepeek.core import _strength


def sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [20, 20, 30, 40, 100, float("inf")],
            "city": ["A", "A", "B", "B", None, "B"],
            "churn": [0, 0, 0, 0, 0, 1],
        }
    )


def test_profile_contains_complete_mvp_without_mutation() -> None:
    df = sample()
    original = df.copy(deep=True)

    report = fp.profile(df, target="churn")

    assert set(report) == {
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
    assert report["target"]["type"] == "categorical"
    assert report["target"]["imbalanced"] is True
    assert report["missing"].attrs["rows"]["rows_with_missing"] == 1
    assert report["correlations"]["matrix"].shape == (2, 2)
    pd.testing.assert_frame_equal(df, original)


def test_edge_cases_return_stable_empty_schemas() -> None:
    categorical_only = pd.DataFrame({"label": ["a", None, "b"]})
    numeric_only = pd.DataFrame({"value": [1, float("inf"), 3]})

    assert fp.numeric(categorical_only).empty
    assert fp.outliers(categorical_only).empty
    assert fp.correlations(categorical_only)["matrix"].empty
    assert fp.categorical(numeric_only).empty
    assert fp.numeric(numeric_only).loc[0, "count"] == 2


def test_validation_and_parameter_errors_are_informative() -> None:
    with pytest.raises(TypeError, match="pandas.DataFrame"):
        fp.validate([])
    with pytest.raises(ValueError, match="at least one row"):
        fp.validate(pd.DataFrame())
    with pytest.raises(ValueError, match="unique"):
        fp.validate(pd.DataFrame([[1, 2]], columns=["x", "x"]))
    with pytest.raises(KeyError, match="missing"):
        fp.target(sample(), "missing")
    with pytest.raises(ValueError, match="pearson"):
        fp.correlations(sample(), method="invalid")


def test_warnings_detect_actionable_quality_issues() -> None:
    df = pd.DataFrame(
        {
            "constant": [1, 1, 1, 1],
            "empty": [None, None, None, None],
            "number_text": ["1", "2", "3", "4"],
        }
    )

    codes = set(fp.warnings(df)["code"])

    assert {"constant", "all_missing", "numeric_as_string"} <= codes


def test_overview_columns_and_missing_cover_supported_types_and_severities() -> None:
    size = 20
    df = pd.DataFrame(
        {
            "number": range(size),
            "flag": [True, False] * 10,
            "when": pd.date_range("2025-01-01", periods=size),
            "label": pd.Series(["a", "b"] * 10, dtype="category"),
            "none": [1] * size,
        }
    )
    df["low"] = [None] + [1] * 19
    df["moderate"] = [None] * 2 + [1] * 18
    df["high"] = [None] * 6 + [1] * 14
    df["critical"] = [None] * 11 + [1] * 9

    metrics = dict(fp.overview(df).itertuples(index=False, name=None))
    column_report = fp.columns(df)
    severities = fp.missing(df).set_index("column")["severity"]

    assert metrics["numeric_columns"] == 6
    assert metrics["boolean_columns"] == 1
    assert metrics["datetime_columns"] == 1
    assert metrics["categorical_columns"] == 1
    assert column_report.set_index("column").loc["number", "possible_id"]
    assert severities[["none", "low", "moderate", "high", "critical"]].tolist() == [
        "none",
        "low",
        "moderate",
        "high",
        "critical",
    ]


def test_duplicate_numeric_categorical_and_outlier_details() -> None:
    df = pd.DataFrame(
        {
            "group": ["a", "a", "b", "b", "c"],
            "value": [1.0, 1.0, 2.0, 2.0, 100.0],
            "flag": [True, True, False, False, True],
        }
    )

    duplicate_report = fp.duplicates(df, subset=["group"], max_examples=2)
    numeric_report = fp.numeric(df).set_index("column")
    category_report = fp.categorical(df, top_n=2).set_index("column")
    outlier_report = fp.outliers(df).set_index("column")

    assert duplicate_report["duplicate_rows"] == 2
    assert duplicate_report["duplicate_groups"] == 2
    assert len(duplicate_report["examples"]) == 2
    assert numeric_report.loc["value", "max"] == 100
    assert category_report.loc["group", "top_categories"] == {"a": 2, "b": 2}
    assert category_report.loc["flag", "unique"] == 2
    assert outlier_report.loc["value", "upper_outliers"] == 1
    assert fp.duplicates(pd.DataFrame({"x": [1, 2]}))["groups"].empty
    assert pd.isna(
        fp.outliers(pd.DataFrame({"x": [float("nan")]})).loc[0, "outlier_count"]
    )


def test_correlations_and_numeric_target() -> None:
    x = pd.Series(range(30), dtype=float)
    df = pd.DataFrame({"x": x, "y": x * 2, "target": x**2})

    correlation_report = fp.correlations(df)
    target_report = fp.target(df, "target")

    assert correlation_report["pairs"].iloc[0]["strength"] == "very strong"
    assert len(fp.correlations(df, threshold=0.99)["pairs"]) >= 1
    assert target_report["type"] == "numeric"
    assert target_report["summary"].loc[0, "column"] == "target"
    assert not target_report["correlations"].empty


def test_zero_correlation_has_no_direction() -> None:
    pairs = fp.correlations(
        pd.DataFrame({"x": [1, 2, 3], "y": [1, 0, 1]})
    )["pairs"]

    assert pairs.loc[0, "correlation"] == 0
    assert pairs.loc[0, "direction"] == "none"


def test_extended_warning_detection() -> None:
    size = 40
    df = pd.DataFrame(
        {
            "near_constant": ["a"] * 39 + ["b"],
            "identifier": [f"id-{value}" for value in range(size)],
            "mostly_missing": [None] * 30 + list(range(10)),
            "date_text": pd.date_range("2025-01-01", periods=size).astype(str),
            "outlier": [0] * 39 + [100],
            "target": [0] * 35 + [1] * 5,
        }
    )
    codes = set(fp.warnings(df, target="target", outlier_threshold=1)["code"])
    duplicate_codes = set(fp.warnings(pd.DataFrame({"x": [1, 1]}))["code"])

    assert {
        "near_constant",
        "possible_identifier",
        "high_cardinality",
        "high_missing",
        "datetime_as_string",
        "potential_outliers",
        "class_imbalance",
    } <= codes
    assert "duplicate_rows" in duplicate_codes


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda: fp.columns(sample(), 0), "high_cardinality_ratio"),
        (lambda: fp.missing(sample(), (20, 5, 50)), "thresholds"),
        (lambda: fp.missing(sample(), (5, 20)), "exactly three"),
        (lambda: fp.duplicates(sample(), max_examples=-1), "max_examples"),
        (lambda: fp.duplicates(sample(), subset=["unknown"]), "Subset"),
        (lambda: fp.duplicates(sample(), subset=[]), "subset"),
        (lambda: fp.categorical(sample(), top_n=0), "top_n"),
        (lambda: fp.outliers(sample(), method="zscore"), "iqr"),
        (lambda: fp.outliers(sample(), multiplier=0), "multiplier"),
        (lambda: fp.correlations(sample(), threshold=2), "threshold"),
        (lambda: fp.target(sample(), "churn", imbalance_ratio=1), "imbalance_ratio"),
        (lambda: fp.warnings(sample(), missing_threshold=-1), "percentage"),
        (lambda: fp.warnings(sample(), near_constant_ratio=0), "near_constant_ratio"),
        (lambda: fp.warnings(sample(), high_cardinality_ratio=2), "high_cardinality"),
    ],
)
def test_invalid_parameters_fail_early(call, message: str) -> None:
    with pytest.raises((KeyError, ValueError), match=message):
        call()


def test_remaining_type_and_correlation_strength_boundaries() -> None:
    df = pd.DataFrame(
        {
            "text": pd.Series(["a", "b"], dtype="string"),
            "duration": pd.to_timedelta([1, 2], unit="D"),
        }
    )
    inferred = fp.columns(df).set_index("column")["inferred_type"]

    assert inferred.to_dict() == {"text": "categorical", "duration": "other"}
    assert [_strength(value) for value in (0.1, 0.3, 0.5, 0.7, 0.9)] == [
        "very weak",
        "weak",
        "moderate",
        "strong",
        "very strong",
    ]
