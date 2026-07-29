from importlib.metadata import version

import pandas as pd
import pytest

import framepeek as fp
import framepeek.report as core
from framepeek.analysis import _strength


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

    report = fp.profile(df, target_column="churn")

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
    assert report["target"]["type"] == "categorical"
    assert report["target"]["imbalanced"] is True
    assert report["missing"]["rows"]["rows_with_missing"] == 1
    assert report["metadata"]["schema_version"] == "1.0"
    assert report["correlations"]["matrix"].shape == (2, 2)
    pd.testing.assert_frame_equal(df, original)


def test_print_report_adds_titles_without_truncating_or_mutating(capsys) -> None:
    long_category = "a-category-value-that-must-remain-completely-visible"
    report = fp.profile(
        pd.DataFrame(
            {
                "number": [1, 2, 3],
                "category": [long_category, "short", "short"],
                "target": [0, 0, 1],
            }
        ),
        target_column="target",
    )
    numeric_before = report["numeric"].copy(deep=True)
    max_colwidth_before = pd.get_option("display.max_colwidth")

    fp.print_report(report, max_rows=100, max_columns=100, max_colwidth=100)
    output = capsys.readouterr().out

    for section in report:
        assert f"=== {section.replace('_', ' ').upper()} ===" in output
    assert "--- MATRIX ---" in output
    assert long_category in output
    assert "..." not in output
    pd.testing.assert_frame_equal(report["numeric"], numeric_before)
    assert pd.get_option("display.max_colwidth") == max_colwidth_before

    fp.print_report({"target": None})
    assert "=== TARGET ===\nNone" in capsys.readouterr().out

    with pytest.raises(TypeError, match="dictionary"):
        fp.print_report([])


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
    severities = fp.missing(df)["columns"].set_index("column")["severity"]

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
    codes = set(
        fp.warnings(df, target_column="target", outlier_threshold=1)["code"]
    )
    duplicate_codes = set(fp.warnings(pd.DataFrame({"x": [1, 1]}))["code"])

    assert {
        "near_constant",
        "possible_identifier",
        "high_cardinality",
        "high_missing",
        "datetime_as_string",
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
        (lambda: fp.warnings(sample(), missing_threshold=-1), "missing_threshold"),
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


def test_profile_reuses_configured_correlation_and_outlier_results(
    monkeypatch,
) -> None:
    x = pd.Series([*range(1, 30), 1000])
    df = pd.DataFrame({"x": x, "target": x**2})
    calls = {"correlations": 0, "outliers": 0}
    original_correlations = core.analysis.correlations
    original_outliers = core.analysis.outliers

    def count_correlations(*args, **kwargs):
        calls["correlations"] += 1
        return original_correlations(*args, **kwargs)

    def count_outliers(*args, **kwargs):
        calls["outliers"] += 1
        return original_outliers(*args, **kwargs)

    monkeypatch.setattr(core.analysis, "correlations", count_correlations)
    monkeypatch.setattr(core.analysis, "outliers", count_outliers)

    report = fp.profile(
        df,
        target_column="target",
        correlation_method="spearman",
        outlier_multiplier=3,
    )

    assert calls == {"correlations": 1, "outliers": 1}
    assert report["target"]["correlations"].equals(
        report["correlations"]["pairs"].query(
            "column_1 == 'target' or column_2 == 'target'"
        ).reset_index(drop=True)
    )
    assert report["target"]["outliers"].equals(
        report["outliers"].query("column == 'target'").reset_index(drop=True)
    )


def test_runtime_version_matches_distribution() -> None:
    assert fp.__version__ == version("framepeek")


def test_profile_warning_uses_configured_outlier_multiplier() -> None:
    df = pd.DataFrame({"value": [*range(20), 100, 101]})

    default_codes = set(fp.profile(df)["warnings"]["code"])
    wide_codes = set(
        fp.profile(df, outlier_multiplier=100)["warnings"]["code"]
    )

    assert "potential_outliers" in default_codes
    assert "potential_outliers" not in wide_codes


@pytest.mark.parametrize("value", [True, False, float("nan"), float("inf"), -float("inf")])
def test_numeric_configuration_rejects_bool_and_non_finite_values(value) -> None:
    expected = TypeError if isinstance(value, bool) else ValueError

    with pytest.raises(expected, match="finite number"):
        fp.outliers(sample(), multiplier=value)
    with pytest.raises(expected, match="finite number"):
        fp.correlations(sample(), threshold=value)
    with pytest.raises(expected, match="finite number"):
        fp.warnings(sample(), near_constant_ratio=value)


@pytest.mark.parametrize(
    ("call", "valid_boundary", "invalid_value"),
    [
        (lambda value: fp.columns(sample(), value), 1, 1.01),
        (lambda value: fp.correlations(sample(), threshold=value), 1, 1.01),
        (lambda value: fp.warnings(sample(), missing_threshold=value), 100, 100.01),
        (lambda value: fp.warnings(sample(), outlier_threshold=value), 100, 100.01),
    ],
)
def test_percentage_and_ratio_upper_boundaries(
    call, valid_boundary, invalid_value
) -> None:
    call(valid_boundary)
    with pytest.raises(ValueError):
        call(invalid_value)


@pytest.mark.parametrize(
    "thresholds",
    [
        (-0.01, 20, 50),
        (0, 20, 100.01),
        (5, 5, 50),
        (20, 5, 50),
        (False, 20, 50),
        (float("nan"), 20, 50),
    ],
)
def test_missing_thresholds_reject_invalid_bounds_and_order(thresholds) -> None:
    with pytest.raises((TypeError, ValueError), match="thresholds"):
        fp.missing(sample(), thresholds)


def test_duplicate_column_diagnostics_and_multiindex_rejection() -> None:
    duplicate = pd.DataFrame([[1, 2, 3]], columns=["id", "id", "value"])
    multiindex = pd.DataFrame(
        [[1, 2]],
        columns=pd.MultiIndex.from_tuples([("a", "x"), ("b", "y")]),
    )

    with pytest.raises(
        ValueError, match=r"'id' \(2 occurrences\)"
    ):
        fp.validate(duplicate)
    with pytest.raises(TypeError, match="single-level Index"):
        fp.validate(multiindex)


@pytest.mark.parametrize(
    "call",
    [
        lambda: fp.duplicates(sample(), max_examples=True),
        lambda: fp.categorical(sample(), top_n=True),
        lambda: fp.categorical(sample(), rare_max_count=False),
    ],
)
def test_integer_configuration_rejects_boolean(call) -> None:
    with pytest.raises(TypeError, match="integer"):
        call()


def test_method_configuration_requires_string() -> None:
    with pytest.raises(TypeError, match="string"):
        fp.outliers(sample(), method=True)


def test_validation_error_classes_distinguish_input_column_and_configuration() -> None:
    with pytest.raises(TypeError):
        fp.validate([])
    with pytest.raises(KeyError):
        fp.target(sample(), "unknown")
    with pytest.raises(ValueError):
        fp.correlations(sample(), threshold=2)


def test_profile_builds_column_metadata_once(monkeypatch) -> None:
    original = core.AnalysisContext.from_frame
    calls = 0

    def count_context(df):
        nonlocal calls
        calls += 1
        return original(df)

    monkeypatch.setattr(core.AnalysisContext, "from_frame", count_context)

    report = fp.profile(sample(), target_column="churn")

    assert calls == 1
    assert report["columns"].set_index("column").loc["city", "missing"] == 1


def test_target_type_overrides_low_cardinality_numeric_inference() -> None:
    df = pd.DataFrame({"feature": range(6), "target": [0, 1, 0, 1, 0, 1]})

    automatic = fp.target(df, "target")
    numeric = fp.target(df, "target", target_type="numeric")
    categorical = fp.profile(
        df, target_column="feature", target_type="categorical"
    )["target"]

    assert automatic["type"] == "categorical"
    assert numeric["type"] == "numeric"
    assert categorical is not None and categorical["type"] == "categorical"

    with pytest.raises(ValueError, match="target_type"):
        fp.target(df, "target", target_type="invalid")


def test_non_finite_statistics_are_separate_from_missing_values() -> None:
    df = pd.DataFrame(
        {"value": [None, float("inf"), -float("inf"), 1.0]}
    )
    row = fp.numeric(df).iloc[0]

    assert row["count"] == 1
    assert row["missing"] == 1
    assert row["non_finite"] == 2
    assert row["positive_infinity"] == 1
    assert row["negative_infinity"] == 1
    assert "non_finite_values" in set(fp.warnings(df)["code"])


def test_outlier_limitations_are_explicit() -> None:
    result = fp.outliers(
        pd.DataFrame({"constant": [1] * 5, "small": [1, 2, None, None, None]})
    ).set_index("column")

    assert result.loc["constant", "limitation"] == "zero_iqr"
    assert result.loc["constant", "applicable"] == False  # noqa: E712
    assert result.loc["small", "limitation"] == "insufficient_sample"


def test_text_and_category_quality_warnings() -> None:
    df = pd.DataFrame(
        {
            "text": [" A", "a", "", " ", "rare"],
            "numeric_id": ["00101", "00102", "00103", "00104", "00105"],
            "mixed": ["a", 1, {"x": 1}, ["b"], None],
        }
    )
    codes = set(
        fp.warnings(
            df,
            rare_max_count=1,
            rare_concentration_ratio=0.2,
        )["code"]
    )

    assert {
        "empty_string",
        "surrounding_whitespace",
        "category_case",
        "rare_category_concentration",
        "numeric_identifier",
        "mixed_object_types",
    } <= codes


def test_report_formatting_and_serialization_are_bounded_and_machine_readable(
    capsys,
) -> None:
    report = fp.profile(
        pd.DataFrame(
            {
                "value": [1, float("inf"), float("nan")],
                "when": pd.date_range("2025-01-01", periods=3),
            }
        )
    )

    text = fp.format_report(report, max_rows=1, max_columns=2, max_colwidth=8)
    fp.print_report(report, max_rows=1, max_columns=2, max_colwidth=8)
    serialized = fp.to_serializable(report)

    assert text in capsys.readouterr().out
    assert "..." in text
    assert serialized["numeric"][0]["max"] == 1.0
    assert serialized["metadata"]["schema_version"] == "1.0"
    assert fp.to_serializable(float("inf")) == "Infinity"
    assert fp.to_serializable(float("-inf")) == "-Infinity"
    assert fp.to_serializable(float("nan")) is None
    assert fp.to_serializable(pd.Timestamp("2025-01-01")) == "2025-01-01T00:00:00"
    assert fp.to_serializable(pd.NA) is None
    assert fp.to_serializable({"x": pd.Series([1]).iloc[0]}) == {"x": 1}
    assert fp.to_serializable(object()).startswith("<object object")


def test_warning_sampling_is_reproducible_and_recorded() -> None:
    df = pd.DataFrame({"text": [str(value) for value in range(2000)]})

    first = fp.profile(df, warning_sample_size=100, random_state=7)
    second = fp.profile(df, warning_sample_size=100, random_state=7)

    pd.testing.assert_frame_equal(first["warnings"], second["warnings"])
    assert first["metadata"]["sampling"]["warnings_used"] is True
    assert first["metadata"]["sampling"]["warning_sample_size"] == 100
    assert (
        fp.profile(
            pd.DataFrame({"number": range(2000)}),
            warning_sample_size=100,
        )["metadata"]["sampling"]["warnings_used"]
        is False
    )


def test_correlation_subset_limits_and_pair_options() -> None:
    df = pd.DataFrame({f"x{index}": range(20) for index in range(4)})

    result = fp.correlations(
        df,
        columns=["x0", "x1", "x2"],
        include_matrix=False,
        top_pairs=1,
        sample_rows=10,
        random_state=3,
    )
    skipped = fp.correlations(df, max_columns=2, overflow="skip")

    assert result["matrix"].empty
    assert len(result["pairs"]) == 1
    assert skipped["pairs"].empty
    with pytest.raises(ValueError, match="at most 2"):
        fp.correlations(df, max_columns=2)
    with pytest.raises(KeyError, match="not found"):
        fp.correlations(df, columns=["missing"])
    with pytest.raises(ValueError, match="sample_rows"):
        fp.correlations(
            pd.DataFrame({"x": range(10_001), "y": range(10_001)}),
            method="kendall",
        )
