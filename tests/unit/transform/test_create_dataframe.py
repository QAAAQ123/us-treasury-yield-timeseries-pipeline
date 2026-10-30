from datetime import date

import pandas as pd

from transform import RECORD_KEY_MAP, create_dataframe


def test_all_maturity_records_return_all_maturity_columns():
    fake_records = [
        {
            "date": date(2026, 10, 28),
            "yield_1m": 3.7,
            "yield_1_5m": 3.65,
            "yield_2m": 3.6,
            "yield_3m": 3.55,
            "yield_4m": 3.5,
            "yield_6m": 3.45,
            "yield_1y": 3.4,
            "yield_2y": 3.35,
            "yield_3y": 3.3,
            "yield_5y": 3.25,
            "yield_7y": 3.2,
            "yield_10y": 3.15,
            "yield_20y": 3.1,
            "yield_30y": 3.05,
        }
    ]

    result = create_dataframe(fake_records)

    assert result.columns.tolist() == list(RECORD_KEY_MAP.values())


def test_unsorted_records_return_sorted_dataframe():
    fake_records = [
        {
            "date": date(2026, 10, 30),
            "yield_1m": 3.9,
            "yield_2y": 3.55,
            "yield_10y": 3.35,
        },
        {
            "date": date(2026, 10, 28),
            "yield_1m": 3.7,
            "yield_2y": 3.35,
            "yield_10y": 3.15,
        },
        {
            "date": date(2026, 10, 29),
            "yield_1m": 3.8,
            "yield_2y": 3.45,
            "yield_10y": 3.25,
        },
    ]

    result = create_dataframe(fake_records)

    assert result["date"].tolist() == [
        date(2026, 10, 28),
        date(2026, 10, 29),
        date(2026, 10, 30),
    ]

    assert result["yield_1m"].tolist() == [3.7, 3.8, 3.9]


def test_none_yield_values_return_dataframe_with_nan():
    fake_records = [
        {
            "date": date(2026, 10, 28),
            "yield_1m": None,
            "yield_2y": 3.35,
            "yield_10y": None,
        },
        {
            "date": date(2026, 10, 29),
            "yield_1m": 3.8,
            "yield_2y": None,
            "yield_10y": 3.25,
        },
    ]

    result = create_dataframe(fake_records)

    assert pd.isna(result.loc[0, "yield_1m"])
    assert pd.isna(result.loc[0, "yield_10y"])
    assert pd.isna(result.loc[1, "yield_2y"])


def test_missing_dates_return_absent_in_dataframe():
    fake_records = [
        {
            "date": date(2026, 10, 28),
            "yield_1m": 3.7,
        },
        {
            "date": date(2026, 10, 30),
            "yield_1m": 3.9,
        },
    ]

    result = create_dataframe(fake_records)

    assert result["date"].tolist() == [
        date(2026, 10, 28),
        date(2026, 10, 30),
    ]
