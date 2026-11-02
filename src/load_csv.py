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
    """전체 기간 curve DataFrame으로 curve / spread CSV를 최초 생성한다."""
    curve_df = curve_df.sort_values("date", ignore_index=True)

    _validate(curve_df)
    _save(curve_df)


def update_csv(new_curve_df: pd.DataFrame) -> None:
    """신규 curve DataFrame을 기존 CSV에 날짜 기준 upsert한다."""
    _validate(new_curve_df)

    old_curve_df = pd.read_csv(CURVE_PATH, parse_dates=["date"], dtype=YIELD_DTYPES)
    merged_curve_df = (
        pd.concat([old_curve_df, new_curve_df])
        .drop_duplicates("date", keep="last")
        .sort_values("date", ignore_index=True)
    )

    _validate(merged_curve_df)
    _save(merged_curve_df)


def _validate(df: pd.DataFrame) -> None:
    """컬럼 구성과 date 컬럼의 유효성(결측, 중복, 정렬)을 검증한다."""
    if missing := CURVE_DTYPE_MAP.keys() - df.columns:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df["date"].isna().any():
        raise ValueError("Missing values found in the date column.")
    if df["date"].duplicated().any():
        raise ValueError("Duplicate dates found in the date column.")
    if not df["date"].is_monotonic_increasing:
        raise ValueError("Dates are not sorted in ascending order.")


def _save(curve_df: pd.DataFrame) -> None:
    """curve와 spread를 각각의 CSV로 저장한다."""
    outputs = {CURVE_PATH: curve_df, SPREAD_PATH: _to_spread(curve_df)}
    for path, df in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)


def _to_spread(curve_df: pd.DataFrame) -> pd.DataFrame:
    """Yield curve DataFrame으로 Yield spread DataFrame을 생성한다."""
    return curve_df[["date"]].assign(
        spread_10y_2y=curve_df["yield_10y"] - curve_df["yield_2y"],
        spread_10y_3m=curve_df["yield_10y"] - curve_df["yield_3m"],
    )
