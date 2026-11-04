import pandas as pd
import pytest

import load_csv
from extract import fetch_yield_curve_archive_xml
from load_csv import CURVE_DTYPE_MAP, initialize_csv
from transform import parse_yield_curve_records, create_yield_curve_dataframe


@pytest.mark.integration
def test_save_initial_csv_with_real_data(tmp_path, monkeypatch):
    curve_path = tmp_path / "yield_curve" / "yield_curve.csv"
    spread_path = tmp_path / "yield_spread" / "yield_spread.csv"

    monkeypatch.setattr(load_csv, "CURVE_PATH", curve_path)
    monkeypatch.setattr(load_csv, "SPREAD_PATH", spread_path)

    response = fetch_yield_curve_archive_xml(2000, 2009)
    records = parse_yield_curve_records(response)
    curve_df = create_yield_curve_dataframe(records)

    initialize_csv(curve_df)

    assert curve_path.exists()
    assert spread_path.exists()

    saved_curve_df = pd.read_csv(curve_path, parse_dates=["date"])
    saved_spread_df = pd.read_csv(spread_path, parse_dates=["date"])

    # Curve CSV 검증
    assert list(saved_curve_df.columns) == list(CURVE_DTYPE_MAP)
    assert len(saved_curve_df) == len(records)
    assert saved_curve_df["date"].is_monotonic_increasing
    assert not saved_curve_df["date"].duplicated().any()

    # Spread CSV 검증
    assert list(saved_spread_df.columns) == [
        "date",
        "spread_10y_2y",
        "spread_10y_3m",
    ]
    pd.testing.assert_series_equal(
        saved_spread_df["date"], saved_curve_df["date"]
    )
    pd.testing.assert_series_equal(
        saved_spread_df["spread_10y_2y"],
        (saved_curve_df["yield_10y"] - saved_curve_df["yield_2y"]).rename(
            "spread_10y_2y"
        ),
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )
    pd.testing.assert_series_equal(
        saved_spread_df["spread_10y_3m"],
        (saved_curve_df["yield_10y"] - saved_curve_df["yield_3m"]).rename(
            "spread_10y_3m"
        ),
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )