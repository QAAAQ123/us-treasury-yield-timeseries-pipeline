from datetime import date

import pytest

from extract import _validate_args


@pytest.mark.parametrize(
    "year, month",
    [("2020", None), (2020, "10"), (2020.4, 10), (2020, 10.32)],
)
def test_year_or_month_is_not_expected_type_raises_typeerror(year, month):
    with pytest.raises(TypeError):
        _validate_args(year, month)


def test_year_below_1990_raises_valueerror():
    with pytest.raises(ValueError):
        _validate_args(1989, None)


def test_year_after_current_year_raises_valueerror():
    year = date.today().year + 1

    with pytest.raises(ValueError):
        _validate_args(year, None)


@pytest.mark.parametrize("month", [0, 13])
def test_month_out_of_range_raises_valueerror(month):
    with pytest.raises(ValueError):
        _validate_args(2020, month)


def test_year_and_month_is_in_future_raises_valueerror():
    today = date.today()

    if today.month == 12:
        year, month = today.year + 1, 1
    else:
        year, month = today.year, today.month + 1

    with pytest.raises(ValueError):
        _validate_args(year, month)


def test_month_none_returns_none():
    result = _validate_args(2020, None)

    assert result is None


def test_year_and_month_returns_none():
    result = _validate_args(2020, 10)

    assert result is None
