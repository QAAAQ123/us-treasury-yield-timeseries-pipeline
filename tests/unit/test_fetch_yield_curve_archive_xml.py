from decimal import Decimal

import pytest
import requests

from extract import YIELD_CURVE_ARCHIVE_URL, fetch_yield_curve_archive_xml


@pytest.mark.parametrize(
    "start_year, end_year",
    [
        (1990, 1999),
        (2000, 2009),
        (2010, 2019),
        (2020, 2023),
        (1990, 2023),
    ],
)
def test_200_with_body_returns_bytes(start_year, end_year, requests_mock):
    url = YIELD_CURVE_ARCHIVE_URL.format(
        start=start_year,
        end=end_year,
    )
    requests_mock.get(url, content=b"<data/>", status_code=200)

    result = fetch_yield_curve_archive_xml(start_year, end_year)

    assert result == b"<data/>"
    assert requests_mock.last_request.url == url


@pytest.mark.parametrize(
    "start_year, end_year",
    [
        (1990, 1999),
        (2000, 2009),
        (2010, 2019),
        (2020, 2023),
        (1990, 2023),
    ],
)
def test_200_with_empty_body_returns_none(start_year, end_year, requests_mock):
    url = YIELD_CURVE_ARCHIVE_URL.format(
        start=start_year,
        end=end_year,
    )
    requests_mock.get(url, content=None, status_code=200)

    result = fetch_yield_curve_archive_xml(start_year, end_year)

    assert result is None
    assert requests_mock.last_request.url == url


@pytest.mark.parametrize(
    "status_code",
    [202, 204, 400, 401, 404, 500, 503],
)
def test_non_200_status_raises_httperror(status_code, requests_mock):
    url = YIELD_CURVE_ARCHIVE_URL.format(start=2000, end=2009)
    requests_mock.get(url, status_code=status_code)

    with pytest.raises(requests.HTTPError):
        fetch_yield_curve_archive_xml(2000, 2009)


def test_timeout_raises_readtimeout(requests_mock):
    url = YIELD_CURVE_ARCHIVE_URL.format(start=2020, end=2023)
    requests_mock.get(url, exc=requests.ReadTimeout)

    with pytest.raises(requests.ReadTimeout):
        fetch_yield_curve_archive_xml(2020, 2023)


@pytest.mark.parametrize(
    "start_year, end_year",
    [
        (1989, 1998),
        (1990, 1998),
        (2000, 2010),
        (2023, 2020),
        (2020, 2024),
    ],
)
def test_unsupported_archive_range_raises_valueerror(
    start_year, end_year, requests_mock
):
    with pytest.raises(ValueError):
        fetch_yield_curve_archive_xml(start_year, end_year)

    assert requests_mock.call_count == 0


@pytest.mark.parametrize(
    "start_year, end_year",
    [
        ("1990", 1999),
        (1990, "1999"),
        (1990.5, 1999),
        (1990, Decimal(1999)),
    ],
)
def test_invalid_args_raises_typeerror(start_year, end_year, requests_mock):
    with pytest.raises(TypeError):
        fetch_yield_curve_archive_xml(start_year, end_year)

    assert requests_mock.call_count == 0
