from extract import _setup_params

DATA_PARAM = "daily_treasury_yield_curve"


def test_month_none_returns_yyyy():
    result = _setup_params(2024, None)

    assert result == {"data": DATA_PARAM, "field_tdr_date_value": "2024"}


def test_year_and_month_returns_yyyymm():
    result = _setup_params(2024, 10)

    assert result == {"data": DATA_PARAM, "field_tdr_date_value_month": "202410"}


def test_month_one_digit_returns_zero_padded_yyyymm():
    result = _setup_params(2024, 2)
    assert result == {"data": DATA_PARAM, "field_tdr_date_value_month": "202402"}
