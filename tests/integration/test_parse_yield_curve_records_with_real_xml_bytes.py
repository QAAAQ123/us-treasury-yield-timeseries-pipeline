from datetime import date

import pytest

from extract import fetch_yield_curve_archive_xml, fetch_yield_curve_xml
from transform import parse_yield_curve_records


@pytest.mark.integration
@pytest.mark.parametrize("year, month", [(1990, 1), (2010, 10), (2004, None)])
def test_yield_curve_request_returns_type_transformed_records(year, month):

    response = fetch_yield_curve_xml(year, month)
    records = parse_yield_curve_records(response)

    _assert_transfomed_records(records)


@pytest.mark.integration
@pytest.mark.parametrize("start, end", [(2000, 2009), (1990, 2023)])
def test_yield_curve_archive_request_returns_type_transformed_records(start, end):

    response = fetch_yield_curve_archive_xml(start, end)
    records = parse_yield_curve_records(response)

    _assert_transfomed_records(records)


def _assert_transfomed_records(records):
    assert isinstance(records, list)
    assert len(records) > 0

    dates = []

    for record in records:
        assert isinstance(record["date"], date)
        dates.append(record["date"])

        for key, value in record.items():
            if key == "date":
                continue

            assert isinstance(value, (float, type(None)))

    assert len(dates) == len(set(dates))
