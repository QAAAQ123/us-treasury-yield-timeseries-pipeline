import pytest

from extract import _validate_archive_args


@pytest.mark.parametrize(
    "start, end",
    [("2020", None), (2020, "10"), (2020.4, 2010), (2020, 2010.32)],
)
def test_start_or_end_year_is_not_expected_type_raises_typeerror(start, end):
    with pytest.raises(TypeError):
        _validate_archive_args(start, end)


@pytest.mark.parametrize(
    "start, end",
    [(1980, 1999), (1999, 2000), (2014, 2020), (2026, 2)],
)
def test_start_or_end_year_is_not_supported_archive_range_raises_valueerror(start, end):
    with pytest.raises(ValueError):
        _validate_archive_args(start, end)


@pytest.mark.parametrize(
    "start, end",
    [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2023), (1990, 2023)],
)
def test_start_and_end_year_is_expected_return_none(start, end):
    result = _validate_archive_args(start, end)

    assert result is None
