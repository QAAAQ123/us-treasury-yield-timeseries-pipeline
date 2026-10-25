import pytest

from extract import fetch_yield_curve_archive_xml


@pytest.mark.integration
@pytest.mark.parametrize("start, end", [(2000, 2009), (1990, 2023)])
def test_support_range_valid_returns_non_empty_bytes(start, end):
    result = fetch_yield_curve_archive_xml(start, end)

    assert isinstance(result, bytes)
    assert len(result) > 0
