import pandas as pd
import pytest

from load_csv import _validate


@pytest.mark.parametrize("missing_col", ["date", "yield_1m", "yield_1_5m", "yield_30y"])
def test_missing_columns_raises_value_error(valid_df, missing_col):
    df = valid_df.drop(columns=[missing_col])

    with pytest.raises(ValueError, match="Missing columns"):
        _validate(df)


def test_missing_date_raises_value_error(valid_df):
    valid_df.loc[0, "date"] = pd.NaT

    with pytest.raises(ValueError, match="Missing values found"):
        _validate(valid_df)


def test_duplicate_dates_raises_value_error(valid_df):
    valid_df.loc[1, "date"] = valid_df.loc[0, "date"]

    with pytest.raises(ValueError, match="Duplicate dates found"):
        _validate(valid_df)


def test_not_ascending_dates_raises_value_error(valid_df):
    df = valid_df.iloc[::-1].reset_index(drop=True)

    with pytest.raises(ValueError, match="not sorted in ascending order"):
        _validate(df)


def test_valid_dataframe_passes(valid_df):
    result = _validate(valid_df)

    assert result is None
