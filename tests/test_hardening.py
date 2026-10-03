"""Regression checks for the combined 0.2.3–0.2.8 maintenance release."""

from importlib.metadata import PackageNotFoundError
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import framepeek as fp
from framepeek import _context
from framepeek._context import AnalysisContext


def test_context_defers_frequencies_and_numeric_profile_does_not_retain_them(
    monkeypatch,
):
    calls = []
    original = _context.value_counts

    def record(series):
        calls.append(series.name)
        return original(series)

    monkeypatch.setattr(_context, "value_counts", record)
    df = pd.DataFrame({"number": range(100), "text": ["a", "b"] * 50})
    context = AnalysisContext.from_frame(df)
    assert calls == []
    assert context.columns["number"].unique == 100
    assert calls == []
    fp.profile(df)
    assert calls == ["text"]


@pytest.mark.parametrize("values", [[4, 2, 4, 2, None], [None, None], [3, 1, 2]])
def test_top_frequency_matches_native_counts(values):
    series = pd.Series(values, dtype="Float64")
    expected = series.dropna().value_counts()
    result = fp.columns(series.to_frame("x")).iloc[0]
    assert result.top_frequency == (int(expected.iloc[0]) if len(expected) else 0)
    if len(expected):
        assert result.top == expected.index[0]


@pytest.mark.parametrize("values", [[1, 2, 1], [1.5, 2.5, 1.5]])
def test_mixed_column_top_preserves_serialized_scalar_types(values):
    from framepeek._values import value_counts

    frame = pd.DataFrame({"number": values, "text": ["a", "b", "a"]})
    result = fp.columns(frame)
    expected = result.copy()
    expected.at[0, "top"] = value_counts(frame.number)[0].value
    assert fp.to_serializable(result) == fp.to_serializable(expected)


@pytest.mark.parametrize(
    "shape,probability", [((70000, 3), 0.01), ((80, 129), 0.5), ((1024, 10), 0.5)]
)
def test_missing_patterns_match_exact_reference(shape, probability):
    mask = np.random.default_rng(4).random(shape) < probability
    labels = pd.Index([("column", i) for i in range(shape[1])], tupleize_cols=False)
    frame = pd.DataFrame(np.where(mask, np.nan, 1), columns=labels)
    expected = {}
    for row in mask:
        pattern = tuple(label for label, flag in zip(labels, row) if flag)
        if pattern:
            expected[pattern] = expected.get(pattern, 0) + 1
    expected = sorted(expected.items(), key=lambda item: -item[1])
    result = fp.missing(frame)
    assert (
        list(zip(result["patterns"].missing_columns, result["patterns"].rows))
        == expected
    )
    assert result["rows"]["rows_with_missing"] == int(mask.any(axis=1).sum())


def test_every_row_has_a_different_missing_pattern():
    mask = (np.arange(1, 1024)[:, None] & (1 << np.arange(10))) != 0
    frame = pd.DataFrame(np.where(mask, np.nan, 1.0))
    result = fp.missing(frame)
    assert len(result["patterns"]) == 1023
    assert result["patterns"].rows.eq(1).all()
    assert result["patterns"].missing_columns.tolist() == [
        tuple(np.flatnonzero(row)) for row in mask
    ]


def test_unused_categories_keep_existing_cardinality_and_frequency_contract():
    series = pd.Series(pd.Categorical(["a", "a", None], categories=["a", "b"]))
    context = AnalysisContext.from_frame(series.to_frame("x"))
    metadata = context.columns["x"]
    assert metadata.unique == 2
    assert [(item.value, item.count) for item in metadata.value_counts] == [
        ("a", 2),
        ("b", 0),
    ]
    assert metadata.value_counts is metadata.value_counts
    assert fp.columns(series.to_frame("x")).iloc[0].top_frequency == 2


@pytest.mark.parametrize(
    "texts,expected_size,sampled",
    [
        ([None] * 8 + ["a", "b"], 2, False),
        ([None] * 10, 0, False),
        (["a"] * 10, 3, True),
    ],
)
def test_warning_sampling_records_actual_non_null_execution(
    texts, expected_size, sampled
):
    report = fp.profile(pd.DataFrame({"text": texts}), warning_sample_size=3)
    sampling = report["metadata"]["sampling"]
    assert sampling["warnings_used"] is sampled
    assert sampling["warning_sample_size"] == expected_size
    assert report["metadata"]["configuration"]["warning_sample_size"] == 3


def test_numeric_only_has_no_warning_parse_sample():
    assert (
        fp.profile(pd.DataFrame({"x": range(5)}))["metadata"]["sampling"][
            "warning_sample_size"
        ]
        == 0
    )


def test_source_tree_version_without_distribution(monkeypatch):
    import importlib.metadata

    def absent(name):
        raise PackageNotFoundError(name)

    with monkeypatch.context() as patch:
        patch.setattr(importlib.metadata, "version", absent)
        # Reload the public package and report to exercise both version consumers.
        importlib.reload(fp)
        importlib.reload(importlib.import_module("framepeek.report"))
        source = Path(__file__).resolve().parents[1] / "pyproject.toml"
        assert f'version = "{fp.__version__}"' in source.read_text(encoding="utf-8")
        assert (
            fp.profile(pd.DataFrame({"x": [1]}))["metadata"]["framepeek_version"]
            == fp.__version__
        )
    importlib.reload(fp)
    importlib.reload(importlib.import_module("framepeek.report"))


def test_source_version_missing_from_project_fails_clearly(monkeypatch):
    from framepeek import _version

    def absent(name):
        raise PackageNotFoundError(name)

    monkeypatch.setattr(_version.metadata, "version", absent)
    monkeypatch.setattr(
        Path, "read_text", lambda *args, **kwargs: '[project]\nname = "framepeek"\n'
    )
    with pytest.raises(RuntimeError, match="Missing project version"):
        _version.runtime_version()


@pytest.mark.parametrize("values", [[-3, -2, -1], [-1, 0, 1]])
def test_nonpositive_mean_cv_is_not_applicable(values):
    assert pd.isna(
        fp.numeric(pd.DataFrame({"x": values})).iloc[0].coefficient_of_variation
    )


def test_positive_mean_cv_and_near_zero_iqr():
    frame = pd.DataFrame({"x": [1e-12, 2e-12, 3e-12, 4e-12, 100e-12]})
    row = fp.numeric(frame).iloc[0]
    assert row.coefficient_of_variation == pytest.approx(frame.x.std() / frame.x.mean())
    result = fp.outliers(frame).iloc[0]
    assert result.applicable
    assert result.outlier_count == 1


def test_zero_iqr_counts_are_not_applicable():
    result = fp.profile(pd.DataFrame({"x": [1, 1, 1, 1, 100]}))
    row = result["outliers"].iloc[0]
    assert not row.applicable and row.limitation == "zero_iqr"
    assert (
        row[["outlier_count", "outlier_pct", "lower_outliers", "upper_outliers"]]
        .isna()
        .all()
    )
    assert "potential_outliers" not in set(result["warnings"].code)


@pytest.mark.parametrize(
    "values,code",
    [
        (["01", "2", "3", "4"], "numeric_as_string"),
        (["01", "02", "3", "4"], "numeric_as_string"),
        (["01", "02", "03", "4"], "numeric_identifier"),
        (["1", "2", "3", "4"], "numeric_as_string"),
    ],
)
def test_leading_zero_identifier_requires_majority(values, code):
    codes = set(fp.quality_warnings(pd.DataFrame({"text": values})).code)
    assert code in codes
    assert ({"numeric_identifier", "numeric_as_string"} - {code}).isdisjoint(codes)
