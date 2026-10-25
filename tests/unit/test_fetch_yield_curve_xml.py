from decimal import Decimal

import pytest
import requests

from extract import YIELD_CURVE_URL, fetch_yield_curve_xml


@pytest.mark.parametrize(
    "year, month", [(2020, None), (2020, 10), (1994, 3), (2001, None)]
)
def test_200_with_body_returns_bytes(year, month, requests_mock):
    requests_mock.get(YIELD_CURVE_URL, content=b"<data/>", status_code=200)

    result = fetch_yield_curve_xml(year, month)

    assert result == b"<data/>"
    assert requests_mock.last_request.qs


@pytest.mark.parametrize(
    "year, month", [(2020, None), (2020, 10), (1994, 3), (2001, None)]
)
def test_200_with_empty_body_returns_none(year, month, requests_mock):
    requests_mock.get(YIELD_CURVE_URL, content=None, status_code=200)

    result = fetch_yield_curve_xml(year, month)

    assert result is None
    assert requests_mock.last_request.qs


@pytest.mark.parametrize(
    "status_code",
    [202, 204, 400, 401, 404, 500, 503],
)
def test_non_200_status_raises_httperror(status_code, requests_mock):
    requests_mock.get(YIELD_CURVE_URL, status_code=status_code)

    with pytest.raises(requests.HTTPError):
        fetch_yield_curve_xml(2020, 10)


def test_timeout_raises_readtimeout(requests_mock):
    requests_mock.get(YIELD_CURVE_URL, exc=requests.ReadTimeout)

    with pytest.raises(requests.ReadTimeout):
        fetch_yield_curve_xml(2020, 10)


@pytest.mark.parametrize(
    "year, month",
    [(1800, None), (2020, 13), (2020, 0)],
)
def test_invalid_args_raises_valueerror(year, month, requests_mock):
    with pytest.raises(ValueError):
        fetch_yield_curve_xml(year, month)

    assert requests_mock.call_count == 0


@pytest.mark.parametrize(
    "year, month",
    [("1800", None), (2020.48, 13), (2020, Decimal(30))],
)
def test_invalid_args_raises_typeerror(year, month, requests_mock):
    with pytest.raises(TypeError):
        fetch_yield_curve_xml(year, month)

    assert requests_mock.call_count == 0
