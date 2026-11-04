"""정제된 yield curve DataFrame을 CSV로 최초 적재 / 증분 적재한다."""

from pathlib import Path

import pandas as pd

CURVE_DTYPE_MAP = {
    "date": "datetime64[ns]",
    "yield_1m": "float64",
    "yield_1_5m": "float64",
    "yield_2m": "float64",
    "yield_3m": "float64",
    "yield_4m": "float64",
    "yield_6m": "float64",
    "yield_1y": "float64",
    "yield_2y": "float64",
    "yield_3y": "float64",
    "yield_5y": "float64",
    "yield_7y": "float64",
    "yield_10y": "float64",
    "yield_20y": "float64",
    "yield_30y": "float64",
}

YIELD_DTYPES = {
    field: dtype for field, dtype in CURVE_DTYPE_MAP.items() if field != "date"
}

MART_DIR = Path(__file__).resolve().parents[1] / "data" / "mart"
CURVE_PATH = MART_DIR / "yield_curve" / "yield_curve.csv"
SPREAD_PATH = MART_DIR / "yield_spread" / "yield_spread.csv"


def initialize_csv(curve_df: pd.DataFrame) -> None:
    """전체 기간의 Yield Curve DataFrame으로 Curve 및 Spread CSV를 최초 생성한다.
    Args:
        curve_df: 전체 기간의 Yield Curve DataFrame.
    Raises:
        ValueError: DataFrame의 컬럼 구성 또는 날짜 데이터가 유효하지 않은 경우.
    """
    curve_df = curve_df.sort_values("date", ignore_index=True)

    _validate(curve_df)
    _save(curve_df)


def update_csv(new_curve_df: pd.DataFrame) -> None:
    """신규 Yield Curve DataFrame을 기존 Curve CSV에 날짜 기준으로 병합한다.

    신규 데이터의 유효성을 먼저 검증하고, 기존 데이터와 병합한 뒤
    중복 날짜는 신규 데이터로 대체한다. 병합 결과를 날짜 오름차순으로 정렬하고
    최종 유효성 검증을 거쳐 Curve 및 Spread CSV를 갱신한다.

    Args:
        new_curve_df: 기존 CSV에 추가할 신규 Yield Curve DataFrame.
    Raises:
        ValueError: 신규 데이터 또는 병합 결과의 유효성 검증에 실패한 경우.
    """
    _validate(new_curve_df)

    old_curve_df = pd.read_csv(CURVE_PATH, parse_dates=["date"], dtype=YIELD_DTYPES)
    #merge 후 새로운 날짜가 추가되었는지 확인하는 헬퍼 필요(추가후 단위 테스트 추가)
    merged_curve_df = (
        pd.concat([old_curve_df, new_curve_df])
        .drop_duplicates("date", keep="last")
        .sort_values("date", ignore_index=True)
    )

    _validate(merged_curve_df)
    _save(merged_curve_df)


def _validate(df: pd.DataFrame) -> None:
    """Yield Curve DataFrame의 컬럼 구성과 날짜 데이터의 유효성을 검증한다.

    필수 컬럼 누락, 날짜 결측, 날짜 중복 및 오름차순 정렬 여부를 확인한다.

    Args:
        df: 유효성을 검증할 Yield Curve DataFrame.
    Raises:
        ValueError: 필수 컬럼이 누락되었거나 날짜 데이터가 유효하지 않은 경우.
    """
    if missing := CURVE_DTYPE_MAP.keys() - df.columns:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df["date"].isna().any():
        raise ValueError("Missing values found in the date column.")
    if df["date"].duplicated().any():
        raise ValueError("Duplicate dates found in the date column.")
    if not df["date"].is_monotonic_increasing:
        raise ValueError("Dates are not sorted in ascending order.")


def _save(curve_df: pd.DataFrame) -> None:
    """Yield Curve와 Yield Spread DataFrame을 각각의 CSV 파일로 저장한다.

    저장 경로의 상위 디렉토리가 존재하지 않으면 생성하며,
    동일한 경로에 파일이 존재하는 경우 기존 파일을 덮어쓴다.

    Args:
        curve_df: 저장할 Yield Curve DataFrame.
    """
    outputs = {CURVE_PATH: curve_df, SPREAD_PATH: _to_spread(curve_df)}
    for path, df in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)


def _to_spread(curve_df: pd.DataFrame) -> pd.DataFrame:
    """Yield Curve DataFrame으로부터 Yield Spread DataFrame을 생성한다.

    10년물 금리와 2년물 금리, 3개월물 금리의 차이를 각각 계산한다.

    Args:
        curve_df: Yield Spread 계산에 사용할 Yield Curve DataFrame.
    Returns:
        date, spread_10y_2y, spread_10y_3m 컬럼으로 구성된 DataFrame.
    """
    return curve_df[["date"]].assign(
        spread_10y_2y=curve_df["yield_10y"] - curve_df["yield_2y"],
        spread_10y_3m=curve_df["yield_10y"] - curve_df["yield_3m"],
    )
