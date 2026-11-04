import pandas as pd
import pytest

from load_csv import _to_spread


def test_spread_is_yield_diff(valid_df):
    valid_df["yield_10y"] = [2.0, 1.7]
    valid_df["yield_2y"] = [1.5, 1.3]
    valid_df["yield_3m"] = [1.2, 0.5]

    result = _to_spread(valid_df)

    assert result["spread_10y_2y"].tolist() == pytest.approx([0.5, 0.4])
    assert result["spread_10y_3m"].tolist() == pytest.approx([0.8, 1.2])


def test_spread_df_has_date(valid_df):

    result = _to_spread(valid_df)

    pd.testing.assert_series_equal(result["date"], valid_df["date"])


def test_spread_df_has_expected_columns(valid_df):
    result = _to_spread(valid_df)

    assert list(result.columns) == ["date", "spread_10y_2y", "spread_10y_3m"]
