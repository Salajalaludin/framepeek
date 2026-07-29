import pandas as pd
from hypothesis import given, settings
from hypothesis import strategies as st

import framepeek as fp


@settings(max_examples=25)
@given(
    st.lists(
        st.tuples(
            st.one_of(st.none(), st.integers(-100, 100)),
            st.one_of(st.none(), st.integers(-100, 100)),
        ),
        min_size=2,
        max_size=20,
    )
)
def test_numeric_missing_and_correlation_invariants(rows) -> None:
    df = pd.DataFrame(
        {
            "x": pd.Series([row[0] for row in rows], dtype="Float64"),
            "y": pd.Series([row[1] for row in rows], dtype="Float64"),
        }
    )
    original = df.copy(deep=True)

    report = fp.profile(df)
    numeric = report["numeric"].set_index("column")
    missing = report["missing"]

    assert numeric["count"].to_dict() == {
        name: int(df[name].notna().sum()) for name in df
    }
    assert missing["columns"]["missing"].sum() == int(df.isna().sum().sum())
    assert missing["patterns"]["rows"].sum() == missing["rows"]["rows_with_missing"]
    assert report["correlations"]["matrix"].shape == (2, 2)
    assert report["correlations"]["pairs"].columns.tolist() == [
        "column_1",
        "column_2",
        "correlation",
        "absolute_correlation",
        "direction",
        "strength",
    ]
    pd.testing.assert_frame_equal(df, original)


def test_extension_datetime_and_arrow_dtypes() -> None:
    arrow = pd.Series(["a", None], dtype="string[pyarrow]")
    df = pd.DataFrame(
        {
            "timezone": pd.date_range("2026-01-01", periods=2, tz="UTC"),
            "duration": pd.to_timedelta([1, 2], unit="D"),
            "category": pd.Series(["a", "b"], dtype="category"),
            "arrow": arrow,
        }
    )

    inferred = fp.columns(df).set_index("column")["inferred_type"]

    assert isinstance(arrow.dtype, pd.StringDtype)
    assert arrow.dtype.storage == "pyarrow"
    assert inferred.to_dict() == {
        "timezone": "datetime",
        "duration": "other",
        "category": "categorical",
        "arrow": "categorical",
    }
