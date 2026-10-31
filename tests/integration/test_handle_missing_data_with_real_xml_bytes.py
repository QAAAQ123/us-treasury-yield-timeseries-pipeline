"""
테스트 목적: transform 모듈 parse_yield_curve_records과 missing_data 모듈 handle_missing_data 동작 검증
"""

from datetime import date, timedelta

import pytest

from extract import fetch_yield_curve_archive_xml, fetch_yield_curve_xml
from missing_data import RECORD_KEY_MAP, handle_missing_data
from transform import parse_yield_curve_records

YIELD_KEYS = [value for value in RECORD_KEY_MAP.values() if value.startswith("yield_")]


def _assert_pipeline_result(xml_bytes: bytes):

    assert isinstance(xml_bytes, bytes)
    assert len(xml_bytes) > 0

    records = parse_yield_curve_records(xml_bytes)

    assert len(records) > 0

    source_dates = [record["date"] for record in records]

    # 원본 날짜 검증
    assert all(isinstance(d, date) for d in source_dates)
    assert source_dates == sorted(source_dates)
    assert len(source_dates) == len(set(source_dates))

    result = handle_missing_data(records)

    result_dates = [record["date"] for record in result]

    # 최종 날짜 검증
    assert result_dates == sorted(result_dates)
    assert len(result_dates) == len(set(result_dates))

    # 영업일과 휴장일을 포함한 연속적인 날짜 목록
    expected_dates = [
        source_dates[0] + timedelta(days=offset)
        for offset in range((source_dates[-1] - source_dates[0]).days + 1)
    ]

    assert result_dates == expected_dates

    # 레코드 스키마 및 금리 타입 검증
    for record in result:
        assert "date" in record
        assert all(key in record for key in YIELD_KEYS)

        for key in YIELD_KEYS:
            assert record[key] is None or isinstance(record[key], float)

    # 생성된 날짜의 금리 값 검증
    source_date_set = set(source_dates)
    last_observed_record = None

    for record in result:
        if record["date"] in source_date_set:
            last_observed_record = record
        else:
            assert last_observed_record is not None

            for key in YIELD_KEYS:
                assert record[key] == last_observed_record[key]


@pytest.mark.integration
def test_archive_xml_pipeline_returns_normalized_records():
    xml_bytes = fetch_yield_curve_archive_xml(2000, 2009)

    _assert_pipeline_result(xml_bytes)


@pytest.mark.integration
def test_monthly_xml_pipeline_returns_normalized_records():
    xml_bytes = fetch_yield_curve_xml(2000, 10)

    _assert_pipeline_result(xml_bytes)
