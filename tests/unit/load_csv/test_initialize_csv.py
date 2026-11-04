from unittest.mock import (
    patch,  # pytest-mock 대신 unittest.mock.patch 사용(사용 횟수 적음)
)

import pandas as pd
import pytest

import load_csv
from load_csv import initialize_csv


def test_initialize_csv_sorts_before_validate_and_save():
    unsorted_df = pd.DataFrame(
        {"date": ["2020-10-03", "2020-10-01", "2020-10-02"], "value": [100, 300, 200]}
    )
    sorted_df = pd.DataFrame(
        {"date": ["2020-10-01", "2020-10-02", "2020-10-03"], "value": [300, 200, 100]}
    )

    with (
        patch.object(load_csv, "_validate") as validate_spy,
        patch.object(load_csv, "_save") as save_spy,
    ):
        initialize_csv(unsorted_df)

    validate_spy.assert_called_once()
    save_spy.assert_called_once()
    pd.testing.assert_frame_equal(validate_spy.call_args.args[0], sorted_df)
    pd.testing.assert_frame_equal(save_spy.call_args.args[0], sorted_df)


def test_initialize_csv_does_not_save_when_validation_fails():
    with (
        patch.object(load_csv, "_validate", side_effect=ValueError()) as validate_spy,
        patch.object(load_csv, "_save") as save_spy,
        pytest.raises(ValueError),
    ):
        initialize_csv(pd.DataFrame({"date": ["2020-11-11"]}))

    validate_spy.assert_called_once()
    save_spy.assert_not_called()
