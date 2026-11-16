import numpy as np
import pandas as pd
import pytest

import load_csv
import pipeline
from load_csv import YIELD_DTYPES

SPREAD_DTYPES = {
    "spread_10y_2y": "float64",
    "spread_10y_3m": "float64",
}


def _read_curve_csv(path):
    return pd.read_csv(
        path,
        parse_dates=["date"],
        dtype=YIELD_DTYPES,
    )


def _read_spread_csv(path):
    return pd.read_csv(
        path,
        parse_dates=["date"],
        dtype=SPREAD_DTYPES,
    )


def _assert_frames_close(expected, actual):
    pd.testing.assert_frame_equal(
        expected.reset_index(drop=True),
        actual.reset_index(drop=True),
        check_exact=False,
        rtol=1e-9,
        atol=1e-9,
    )


@pytest.mark.e2e
def test_run_incremental_pipeline_restores_missing_record_and_is_idempotent(
    tmp_path, monkeypatch
):
    """누락된 현재 월 데이터를 복구하고 반복 실행에도 결과가 유지되는지 검증한다."""
    curve_csv = tmp_path / "curve.csv"
    spread_csv = tmp_path / "spread.csv"

    monkeypatch.setattr(load_csv, "CURVE_PATH", curve_csv)
    monkeypatch.setattr(load_csv, "SPREAD_PATH", spread_csv)

    monkeypatch.setattr(pipeline, "CURVE_PATH", curve_csv)
    monkeypatch.setattr(pipeline, "SPREAD_PATH", spread_csv)

    pipeline.run_initial_pipeline()

    snapshot_curve = _read_curve_csv(curve_csv)
    snapshot_spread = _read_spread_csv(spread_csv)

    assert not snapshot_curve.empty
    assert not snapshot_spread.empty

    today = pd.Timestamp(pipeline.TODAY)

    current_month_mask = snapshot_curve["date"].dt.year.eq(today.year) & snapshot_curve[
        "date"
    ].dt.month.eq(today.month)

    if not current_month_mask.any():
        pytest.skip("현재 연월에 해당하는 데이터가 없습니다.")

    target_date = snapshot_curve.loc[current_month_mask, "date"].max()

    target_curve_mask = snapshot_curve["date"].eq(target_date)
    target_spread_mask = snapshot_spread["date"].eq(target_date)

    assert target_curve_mask.sum() == 1
    assert target_spread_mask.sum() == 1

    # 가장 최근 날짜의 레코드를 양쪽 CSV에서 삭제
    snapshot_curve.loc[~target_curve_mask].to_csv(curve_csv, index=False)
    snapshot_spread.loc[~target_spread_mask].to_csv(spread_csv, index=False)

    # 테스트 시작
    pipeline.run_incremental_pipeline()

    curve_after_first = _read_curve_csv(curve_csv)
    spread_after_first = _read_spread_csv(spread_csv)

    # 삭제했던 날짜의 Curve 및 Spread 레코드가 원래 데이터와 동일하게 복구되었는지 검증
    restored_curve = curve_after_first.loc[
        curve_after_first["date"].eq(target_date),
        ["date", *YIELD_DTYPES.keys()],
    ]

    restored_spread = spread_after_first.loc[
        spread_after_first["date"].eq(target_date),
        ["date", *SPREAD_DTYPES.keys()],
    ]

    expected_curve = snapshot_curve.loc[
        target_curve_mask,
        ["date", *YIELD_DTYPES.keys()],
    ]

    expected_spread = snapshot_spread.loc[
        target_spread_mask,
        ["date", *SPREAD_DTYPES.keys()],
    ]

    assert len(restored_curve) == 1
    assert len(restored_spread) == 1

    _assert_frames_close(expected_curve, restored_curve)
    _assert_frames_close(expected_spread, restored_spread)

    expected_spread_values = np.array(
        [
            restored_curve["yield_10y"].iloc[0] - restored_curve["yield_2y"].iloc[0],
            restored_curve["yield_10y"].iloc[0] - restored_curve["yield_3m"].iloc[0],
        ]
    )

    actual_spread_values = (
        restored_spread[["spread_10y_2y", "spread_10y_3m"]].iloc[0].to_numpy()
    )

    np.testing.assert_allclose(
        actual_spread_values,
        expected_spread_values,
        rtol=1e-9,
        atol=1e-9,
        equal_nan=True,
    )

    # 삭제하지 않은 나머지 레코드가 변경되지 않았는지 검증
    _assert_frames_close(
        snapshot_curve.loc[~target_curve_mask],
        curve_after_first.loc[curve_after_first["date"].ne(target_date)],
    )

    _assert_frames_close(
        snapshot_spread.loc[~target_spread_mask],
        spread_after_first.loc[spread_after_first["date"].ne(target_date)],
    )

    # 초기 적재 직후와 행 수 비교
    assert len(curve_after_first) == len(snapshot_curve)
    assert len(spread_after_first) == len(snapshot_spread)

    # 컬럼 스키마 검증
    assert curve_after_first.columns.tolist() == [
        "date",
        *YIELD_DTYPES.keys(),
    ]

    assert spread_after_first.columns.tolist() == [
        "date",
        *SPREAD_DTYPES.keys(),
    ]

    # 날짜 유효성 및 정합성 검증
    for df in (curve_after_first, spread_after_first):
        assert df["date"].notna().all()
        assert df["date"].is_unique
        assert df["date"].is_monotonic_increasing

    pd.testing.assert_series_equal(
        curve_after_first["date"].reset_index(drop=True),
        spread_after_first["date"].reset_index(drop=True),
    )

    # 증분 파이프라인 재실행을 통한 멱등성 검증
    pipeline.run_incremental_pipeline()

    curve_after_second = _read_curve_csv(curve_csv)
    spread_after_second = _read_spread_csv(spread_csv)

    assert len(curve_after_second) == len(curve_after_first)
    assert len(spread_after_second) == len(spread_after_first)

    _assert_frames_close(curve_after_first, curve_after_second)
    _assert_frames_close(spread_after_first, spread_after_second)
