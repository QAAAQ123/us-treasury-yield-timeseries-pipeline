from datetime import date, timedelta

import pytest

from missing_data import RECORD_KEY_MAP, handle_missing_data

"""
test_empty_records_returns_empty_list: []를 넣으면 []가 나온다.
test_consecutive_days_returns_same_number_of_records: 달력상 하루 간격으로 연속된 2개, 3개 레코드를 넣으면 개수가 그대로다.
test_missing_yield_fields_are_filled_with_none: 일부 yield_* 키가 없는 레코드를 넣으면 누락된 키가 None으로 채워진다.
test_policy_violation_value_is_changed_to_none: 정책 기간 날짜에 float 값이 있으면 None으로 바뀐다.
test_holiday_gap_inserts_records_copied_from_last_observed_record: 영업일 사이에 휴장일이 1~3일 있으면 그 날짜의 레코드가 추가되고, 값은 직전 관측 레코드를 복사한다.
test_multiple_holiday_gaps_copy_from_each_last_observed_record: 공백이 두 번 있을 때 각 휴장일이 자기 직전 관측 레코드의 값을 복사한다.
"""
YIELD_KEYS = [v for v in RECORD_KEY_MAP.values() if v.startswith("yield_")]


def _make_record(d, **overrides):
    record = {"date": d, **{k: 4.5 for k in YIELD_KEYS}}
    record.update(overrides)
    return record


def test_empty_records_returns_empty_list():
    fake_records = []

    result = handle_missing_data(fake_records)

    assert result == []


@pytest.mark.parametrize(
    "dates",
    [
        [date(2026, 10, 13), date(2026, 10, 14)],
        [date(2026, 10, 13), date(2026, 10, 14), date(2026, 10, 15)],
    ],
)
def test_consecutive_days_returns_same_number_of_records(dates):
    fake_records = [_make_record(day) for day in dates]
    expected = [record for record in fake_records]

    result = handle_missing_data(fake_records)

    assert expected == result


@pytest.mark.parametrize(
    "existing_maturities",
    [["yield_1m"], ["yield_1m", "yield_30y"], ["yield_1m", "yield_1_5_m", "yield_20y"]],
)
def test_missing_yield_fields_are_filled_with_none(existing_maturities):
    fake_record = [
        {
            "date": date(2026, 3, 10),
            **{key: 3.4 for key in existing_maturities},
        }
    ]

    result = handle_missing_data(fake_record)

    for key in YIELD_KEYS:
        assert key in result[0]
        if key not in existing_maturities:
            assert result[0][key] is None


def test_available_from_violation_value_is_changed_to_none():
    # MATURITY_AVAILABLE_FROM
    fake_record = _make_record(date(2018, 10, 15))

    result = handle_missing_data([fake_record])[0]

    assert result["yield_2m"] is None


def test_unavailable_period_violation_value_is_changed_to_none():
    # MATURITY_UNAVAILABLE_PERIODS
    fake_record = _make_record(date(2002, 3, 1))

    result = handle_missing_data([fake_record])[0]

    assert result["yield_30y"] is None


@pytest.mark.parametrize(
    "dates",
    [
        [date(2026, 10, 16), date(2026, 10, 18)],
        [date(2026, 1, 14), date(2026, 1, 18)],
    ],
)
def test_holiday_gap_inserts_records_copied_from_last_observed_record(dates):
    first, last = dates
    fake_records = [_make_record(first), _make_record(last)]
    stub_last_observed_yields = {
        k: v for k, v in fake_records[0].items() if k.startswith("yield_")
    }

    result = handle_missing_data(fake_records)

    holiday_dates = {first + timedelta(days=i) for i in range(1, (last - first).days)}
    result_by_date = {record["date"]: record for record in result}

    assert set(result_by_date) == {first, last} | holiday_dates
    for holiday_date in holiday_dates:
        result_yields = {
            k: v
            for k, v in result_by_date[holiday_date].items()
            if k.startswith("yield_")
        }
        assert result_yields == stub_last_observed_yields


def test_multiple_holiday_gaps_copy_from_each_last_observed_record():
    first_date = date(2026, 1, 5)
    second_date = date(2026, 1, 8)
    third_date = date(2026, 1, 11)

    fake_records = [
        _make_record(first_date, **{k: 4.0 for k in YIELD_KEYS}),
        _make_record(second_date, **{k: 5.0 for k in YIELD_KEYS}),
        _make_record(third_date, **{k: 6.0 for k in YIELD_KEYS}),
    ]

    result = handle_missing_data(fake_records)

    result_by_date = {record["date"]: record for record in result}
    expected_dates = {
        first_date,
        second_date,
        third_date,
        date(2026, 1, 6),
        date(2026, 1, 7),
        date(2026, 1, 9),
        date(2026, 1, 10),
    }
    assert set(result_by_date) == expected_dates

    for holiday_date in (date(2026, 1, 6), date(2026, 1, 7)):
        assert result_by_date[holiday_date]["yield_1m"] == 4.0

    for holiday_date in (date(2026, 1, 9), date(2026, 1, 10)):
        assert result_by_date[holiday_date]["yield_1m"] == 5.0
