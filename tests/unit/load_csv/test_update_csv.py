from unittest.mock import patch

import pandas as pd
import pytest

import load_csv
from load_csv import update_csv


def _df(dates, values):
    return pd.DataFrame({"date": pd.to_datetime(dates), "value": values})


@pytest.fixture
def old_df():
    return _df(["2020-10-01", "2020-10-02"], [100, 200])


@pytest.fixture
def spies(old_df):
    with (
        patch.object(load_csv, "_validate") as validate,
        patch.object(load_csv, "_save") as save,
        patch.object(load_csv.pd, "read_csv", return_value=old_df) as read_csv,
    ):
        yield validate, save, read_csv


def test_existing_date_returns_overwritten_value_on_save(spies):
    _, save, _ = spies

    update_csv(_df(["2020-10-02"], [999]))

    expected = _df(["2020-10-01", "2020-10-02"], [100, 999])
    pd.testing.assert_frame_equal(save.call_args.args[0], expected)


def test_new_dates_returns_sorted_merged_df_on_save(spies):
    _, save, _ = spies

    update_csv(_df(["2020-10-04", "2020-10-03"], [400, 300]))

    expected = _df(
        ["2020-10-01", "2020-10-02", "2020-10-03", "2020-10-04"],
        [100, 200, 300, 400],
    )
    pd.testing.assert_frame_equal(save.call_args.args[0], expected)


def test_new_df_validation_failure_raises_error_without_reading_csv(spies):
    validate, save, read_csv = spies
    validate.side_effect = ValueError("invalid")

    with pytest.raises(ValueError):
        update_csv(_df(["2020-10-03"], [300]))

    read_csv.assert_not_called()
    save.assert_not_called()


def test_merged_df_validation_failure_raises_error_without_saving(spies):
    validate, save, _ = spies
    validate.side_effect = [None, ValueError("invalid")]

    with pytest.raises(ValueError):
        update_csv(_df(["2020-10-03"], [300]))

    assert validate.call_count == 2
    save.assert_not_called()
