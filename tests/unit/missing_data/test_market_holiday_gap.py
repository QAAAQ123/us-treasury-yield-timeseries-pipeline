from datetime import date

import pytest

from missing_data import _has_market_holiday_gap


def test_consecutive_days_return_false():
    result = _has_market_holiday_gap(date(2026, 10, 30), date(2026, 10, 29))

    assert result is False


def test_gap_of_two_or_more_days_returns_true():
    result = _has_market_holiday_gap(date(2026, 10, 30), date(2026, 10, 27))

    assert result is True


@pytest.mark.parametrize(
    "current_date, last_observed_date",
    [
        (date(2026, 10, 29), date(2026, 10, 30)),  # 이전 날짜
        (date(2026, 10, 30), date(2026, 10, 30)),  # 같은 날짜
    ],
)
def test_current_date_not_after_last_observed_raises_value_error(
    current_date, last_observed_date
):
    with pytest.raises(ValueError):
        _has_market_holiday_gap(current_date, last_observed_date)
