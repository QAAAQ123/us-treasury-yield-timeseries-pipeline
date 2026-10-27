from transform import _transform_types

import logging
from datetime import date

import pytest



def test_unmapped_field_logs_warning(caplog):
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "UNEXPECTED_FIELD": "unexpected",
        }
    ]

    with caplog.at_level(logging.WARNING):
        result = _transform_types(records)

    assert result == [{"date": date(2026, 10, 27)}]
    assert "예상하지 못한 필드: UNEXPECTED_FIELD" in caplog.text


def test_empty_date_value_raises_value_error():
    records = [{"NEW_DATE": " ", "BC_1MONTH": "3.8"}]

    with pytest.raises(
        ValueError, match="observation date is missing"
    ):
        _transform_types(records)


def test_record_without_date_raises_value_error():
    records = [{"BC_1MONTH": "3.8"}]

    with pytest.raises(
        ValueError,
        match="record does not contain a valid observation date",
    ):
        _transform_types(records)


def test_empty_yield_value_returns_none():
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": "",
        }
    ]

    result = _transform_types(records)

    assert result == [
        {
            "date": date(2026, 10, 27),
            "yield_1m": None,
        }
    ]


def test_non_numeric_yield_value_raises_value_error():
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": "invalid",
        }
    ]

    with pytest.raises(ValueError):
        _transform_types(records)


def test_empty_records_return_empty_list():
    records = []

    result = _transform_types(records)

    assert result == []


def test_valid_records_return_typed_values():
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


def test_excluded_fields_are_ignored_without_warning(caplog):
    records = [
        {
            "NEW_DATE": "2026-10-27",
            "BC_1MONTH": "3.8",
            "Id": "1",
            "BC_30YEARDISPLAY": "4.5",
        }
    ]

    with caplog.at_level(logging.WARNING):
        result = _transform_types(records)

    assert result == [
        {
            "date": date(2026, 10, 27),
            "yield_1m": 3.8,
        }
    ]
    assert not caplog.records


def test_invalid_date_format_raises_value_error():
    records = [
        {
            "NEW_DATE": "not-a-date",
            "BC_1MONTH": "3.8",
        }
    ]

    with pytest.raises(ValueError):
        _transform_types(records)