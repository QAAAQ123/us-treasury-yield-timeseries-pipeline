import pandas as pd
import pytest

import load_csv
from extract import fetch_yield_curve_xml
from load_csv import CURVE_DTYPE_MAP, initialize_csv, update_csv
from transform import create_yield_curve_dataframe, parse_yield_curve_records


@pytest.mark.integration
def test_update_csv_with_real_data(tmp_path, monkeypatch):
    curve_path = tmp_path / "yield_curve" / "yield_curve.csv"
    spread_path = tmp_path / "yield_spread" / "yield_spread.csv"

    monkeypatch.setattr(load_csv, "CURVE_PATH", curve_path)
    monkeypatch.setattr(load_csv, "SPREAD_PATH", spread_path)

    # 2025년 10월 데이터 수집 및 변환
    response = fetch_yield_curve_xml(2025, 10)
    records = parse_yield_curve_records(response)
    curve_df = create_yield_curve_dataframe(records)

    # 10월 29일까지의 데이터로 초기 CSV 생성
    initial_curve_df = curve_df[
        pd.to_datetime(curve_df["date"]) <= pd.Timestamp("2025-10-29")
    ].copy()

    initialize_csv(initial_curve_df)

    # 2025년 10월 데이터 재수집 및 증분 적재
    response = fetch_yield_curve_xml(2025, 10)
    records = parse_yield_curve_records(response)
    new_curve_df = create_yield_curve_dataframe(records)

    update_csv(new_curve_df)

    assert curve_path.exists()
    assert spread_path.exists()

    saved_curve_df = pd.read_csv(curve_path, parse_dates=["date"])
    saved_spread_df = pd.read_csv(spread_path, parse_dates=["date"])

    # Curve CSV 검증
    assert list(saved_curve_df.columns) == list(CURVE_DTYPE_MAP)
    assert saved_curve_df["date"].is_monotonic_increasing
    assert not saved_curve_df["date"].duplicated().any()

    initial_dates = set(pd.to_datetime(initial_curve_df["date"]))
    saved_dates = set(saved_curve_df["date"])

    assert initial_dates.issubset(saved_dates)
    assert pd.Timestamp("2025-10-30") not in initial_dates
    assert pd.Timestamp("2025-10-31") not in initial_dates
    assert pd.Timestamp("2025-10-30") in saved_dates
    assert pd.Timestamp("2025-10-31") in saved_dates

    # 재수집한 전체 데이터와 최종 CSV 비교
    expected_curve_df = new_curve_df.copy()
    expected_curve_df["date"] = pd.to_datetime(expected_curve_df["date"])

    pd.testing.assert_frame_equal(
        saved_curve_df,
        expected_curve_df,
        check_dtype=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )

    # Spread CSV 검증
    assert list(saved_spread_df.columns) == [
        "date",
        "spread_10y_2y",
        "spread_10y_3m",
    ]
    pd.testing.assert_series_equal(saved_spread_df["date"], saved_curve_df["date"])
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
