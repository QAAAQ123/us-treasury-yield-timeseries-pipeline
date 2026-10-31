import logging
from datetime import date

import pytest

from missing_data import RECORD_KEY_MAP, _apply_treasury_note_policy

YIELD_KEYS = [v for v in RECORD_KEY_MAP.values() if v.startswith("yield_")]


def _make_record(d, **overrides):
    record = {"date": d, **{k: 4.5 for k in YIELD_KEYS}}
    record.update(overrides)
    return record


BOUNDARY_CASES = [
    ("yield_1_5m", date(2025, 2, 17), None),
    ("yield_1_5m", date(2025, 2, 18), 4.5),
    ("yield_2m", date(2018, 10, 15), None),
    ("yield_2m", date(2018, 10, 16), 4.5),
    ("yield_4m", date(2022, 10, 18), None),
    ("yield_4m", date(2022, 10, 19), 4.5),
    ("yield_20y", date(1993, 9, 30), None),
    ("yield_20y", date(1993, 10, 1), 4.5),
    ("yield_30y", date(2002, 2, 17), 4.5),
    ("yield_30y", date(2002, 2, 18), None),
    ("yield_30y", date(2006, 2, 8), None),
    ("yield_30y", date(2006, 2, 9), 4.5),
]


@pytest.mark.parametrize(("maturity", "day", "expected"), BOUNDARY_CASES)
def test_policy_corrects_violating_values(maturity, day, expected):
    """입력이 전부 float여도 정책 기간의 값은 None으로 보정된다"""
    result = _apply_treasury_note_policy(_make_record(day))

    assert result[maturity] == expected


@pytest.mark.parametrize(("maturity", "day", "expected"), BOUNDARY_CASES)
def test_policy_keeps_valid_record_unchanged(maturity, day, expected, caplog):
    """이미 올바른 값(None 또는 float)이 들어오면 그대로 두고 로그도 없다"""
    record = _make_record(day, **{maturity: expected})

    with caplog.at_level(logging.DEBUG):
        result = _apply_treasury_note_policy(record)

    assert result[maturity] == expected
    assert maturity not in caplog.text


def test_available_from_violation_is_logged(caplog):
    with caplog.at_level(logging.DEBUG):
        _apply_treasury_note_policy(_make_record(date(2018, 10, 15)))

    assert "yield_2m" in caplog.text
    assert "2018-10-15" in caplog.text


def test_unavailable_period_violation_is_logged(caplog):
    with caplog.at_level(logging.DEBUG):
        _apply_treasury_note_policy(_make_record(date(2002, 3, 1)))

    assert "yield_30y" in caplog.text
    assert "2002-03-01" in caplog.text
