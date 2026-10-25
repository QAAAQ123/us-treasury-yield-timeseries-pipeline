import pytest

from extract import fetch_response


@pytest.mark.integration
@pytest.mark.parametrize("year", [1990, 2010])
def test_year_only_returns_non_empty_bytes(year):
    result = fetch_response(year)

    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.integration
@pytest.mark.parametrize("year, month", [(1990, 1), (2010, 10)])
def test_year_and_month_returns_non_empty_bytes(year, month):
    result = fetch_response(year, month)

    assert isinstance(result, bytes)
    assert len(result) > 0
