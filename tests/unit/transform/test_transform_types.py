from datetime import date

import pytest

from transform import _transform_types


def test_one_records_return_typed_values():
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": "3.8",
        }
    ]

    result = _transform_types(records)

    assert result == [
        {
            "date": date(2026, 10, 27),
            "yield_1m": 3.8,
        }
    ]


def test_multiple_records_return_preserve_input_order():
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": "3.8",
        },
        {
            "NEW_DATE": "2026-10-28",
            "BC_1MONTH": "3.9",
        },
    ]

    result = _transform_types(records)

    assert result == [
        {
            "date": date(2026, 10, 27),
            "yield_1m": 3.8,
        },
        {
            "date": date(2026, 10, 28),
            "yield_1m": 3.9,
        },
    ]


def test_whitespace_values_are_stripped_before_conversion():
    records = [
        {
            "NEW_DATE": " 2026-10-27 ",
            "BC_1MONTH": " 3.8 ",
        }
    ]

    result = _transform_types(records)

    assert result == [
        {
            "date": date(2026, 10, 27),
            "yield_1m": 3.8,
        }
    ]


@pytest.mark.parametrize("value", ["", " ", "   ", "\t"])
def test_empty_or_whitespace_yield_values_return_none(value):
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": value,
        }
    ]

    result = _transform_types(records)

    assert result == [
        {
            "date": date(2026, 10, 27),
            "yield_1m": None,
        }
    ]


@pytest.mark.parametrize(
    "value",
    ["", " ", "not-a-date", "2026-02-30"],
)
def test_invalid_date_values_raise_value_error(value):
    records = [
        {
            "NEW_DATE": value,
            "BC_1MONTH": "3.8",
        }
    ]

    with pytest.raises(ValueError):
        _transform_types(records)


def test_non_numeric_yield_values_raise_value_error():
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": "invalid",
        }
    ]

    with pytest.raises(ValueError):
        _transform_types(records)


def test_unmapped_fields_are_ignored():
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": "3.8",
            "UNEXPECTED_FIELD": "unexpected",
            "Id": "1",
            "BC_30YEARDISPLAY": "4.5",
        }
    ]

    result = _transform_types(records)

    assert result == [
        {
            "date": date(2026, 10, 27),
            "yield_1m": 3.8,
        }
    ]


def test_empty_records_return_empty_list():
    records = []

    result = _transform_types(records)

    assert result == []


def test_record_without_date_returns_record_without_date():
    records = [
        {
            "BC_1MONTH": "3.8",
        }
    ]

    result = _transform_types(records)

    assert result == [
        {
            "yield_1m": 3.8,
        }
    ]