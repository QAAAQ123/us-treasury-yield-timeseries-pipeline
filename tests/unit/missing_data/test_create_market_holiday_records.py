from datetime import date

import pytest

from missing_data import _create_market_holiday_records


@pytest.mark.parametrize(
    "holiday_dates",
    [
        [date(2023, 2, 10), date(2023, 2, 11)],
        [date(2023, 2, 11)],
        [date(2023, 2, 11), date(2023, 2, 12), date(2023, 2, 13)],
    ],
)
def test_holiday_records_copy_last_observed_yields(holiday_dates):
    last_observed_record = {
        "date": date(2023, 2, 8),
        "yield_1m": 3.4,
        "yield_10y": 3.9,
    }

    result = _create_market_holiday_records(last_observed_record, holiday_dates)

    assert [record["date"] for record in result] == holiday_dates
    for record in result:
        assert record["yield_1m"] == 3.4
        assert record["yield_10y"] == 3.9
