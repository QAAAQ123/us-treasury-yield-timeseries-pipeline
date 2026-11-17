import numpy as np
import pandas as pd
import pytest
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

import load_csv
import pipeline
from load_csv import YIELD_DTYPES


@pytest.mark.e2e
def test_run_initial_pipeline_creates_valid_csv_and_html(tmp_path, monkeypatch):
    """실제 API 데이터를 수집하여 CSV 생성 및 시각화 HTML 문자열을 정상 반환한다."""
    curve_csv = tmp_path / "curve.csv"
    spread_csv = tmp_path / "spread.csv"

    monkeypatch.setattr(load_csv, "CURVE_PATH", curve_csv)
    monkeypatch.setattr(load_csv, "SPREAD_PATH", spread_csv)

    monkeypatch.setattr(pipeline, "CURVE_PATH", curve_csv)
    monkeypatch.setattr(pipeline, "SPREAD_PATH", spread_csv)

    # 테스트 시작
    pipeline.run_initial_pipeline()

    # CSV 파일 생성 및 데이터 존재 여부 검증
    assert curve_csv.is_file()
    assert spread_csv.is_file()
    assert curve_csv.stat().st_size > 0
    assert spread_csv.stat().st_size > 0

    curve_df = pd.read_csv(curve_csv, parse_dates=["date"])
    spread_df = pd.read_csv(spread_csv, parse_dates=["date"])

    assert not curve_df.empty
    assert not spread_df.empty

    # CSV 스키마 및 데이터 타입 검증
    assert curve_df.columns.tolist() == ["date", *YIELD_DTYPES.keys()]
    assert spread_df.columns.tolist() == [
        "date",
        "spread_10y_2y",
        "spread_10y_3m",
    ]

    # 날짜 무결성 검증
    assert is_datetime64_any_dtype(curve_df["date"])
    assert is_datetime64_any_dtype(spread_df["date"])

    assert curve_df["date"].notna().all()
    assert spread_df["date"].notna().all()

    assert not curve_df["date"].duplicated().any()
    assert not spread_df["date"].duplicated().any()

    assert curve_df["date"].is_monotonic_increasing
    assert spread_df["date"].is_monotonic_increasing

    curve_numeric_columns = curve_df.columns.drop("date")
    spread_numeric_columns = spread_df.columns.drop("date")

    assert all(is_numeric_dtype(curve_df[column]) for column in curve_numeric_columns)
    assert all(is_numeric_dtype(spread_df[column]) for column in spread_numeric_columns)

    # Yield Curve와 Yield Spread의 날짜 일치 여부 검증
    pd.testing.assert_series_equal(
        curve_df["date"],
        spread_df["date"],
    )

    # Yield Spread 계산 결과 검증
    np.testing.assert_allclose(
        spread_df["spread_10y_2y"].to_numpy(),
        (curve_df["yield_10y"] - curve_df["yield_2y"]).to_numpy(),
        rtol=0,
        atol=1e-9,
        equal_nan=True,
    )

    # Treasury 금리 발표 정책에 따른 결측 정책 검증
    np.testing.assert_allclose(
        spread_df["spread_10y_3m"].to_numpy(),
        (curve_df["yield_10y"] - curve_df["yield_3m"]).to_numpy(),
        rtol=0,
        atol=1e-9,
        equal_nan=True,
    )

    expected_missing_values = {
        "yield_1_5m": "2025-02-17",
        "yield_2m": "2018-10-15",
        "yield_4m": "2022-10-18",
        "yield_20y": "1992-01-02",
        "yield_30y": "2004-01-02",
    }

    for column, expected_date in expected_missing_values.items():
        date_mask = curve_df["date"].eq(pd.Timestamp(expected_date))
        target_values = curve_df.loc[date_mask, column]

        assert len(target_values) == 1
        assert target_values.isna().all()

    # 달력 공백 날짜의 이전 관측값 복사 여부 검증
    previous_values = (
        curve_df.loc[curve_df["date"].eq(pd.Timestamp("2024-01-05"))]
        .drop(columns="date")
        .reset_index(drop=True)
    )

    gap_values = (
        curve_df.loc[curve_df["date"].eq(pd.Timestamp("2024-01-06"))]
        .drop(columns="date")
        .reset_index(drop=True)
    )

    assert len(previous_values) == 1
    assert len(gap_values) == 1

    pd.testing.assert_frame_equal(gap_values, previous_values)
