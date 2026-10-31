from datetime import date

from missing_data import RECORD_KEY_MAP, _fill_missing_maturities

YIELD_KEYS = [k for k in RECORD_KEY_MAP.values() if k.startswith("yield_")]


def test_all_yield_values_already_has_float_returns_input_record():
    fake_record = {"date": date(2026, 1, 2), **{k: 4.5 for k in YIELD_KEYS}}

    result = _fill_missing_maturities(fake_record)

    assert result == fake_record


def test_some_yield_key_not_exist_returns_fill_none_value():
    record = {"date": date(2026, 1, 2), "yield_1m": 4.5}

    result = _fill_missing_maturities(record)

    assert result["yield_1m"] == 4.5
    for key in YIELD_KEYS:
        assert key in result
        if key != "yield_1m":
            assert result[key] is None
