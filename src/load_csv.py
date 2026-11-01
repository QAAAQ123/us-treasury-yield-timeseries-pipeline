"""
정제된 데이테 프레임을 활용해서 지정된 디렉토리로 CSV 적재 및 CSV 증분 적재 수행
"""

from pathlib import Path

import pandas as pd

CURVE_DTYPE_MAP = {
    "date": "object",
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

SPREAD_DTYPE_MAP = {
    "date": "object",
    "spread_10y_2y": "float64",
    "spread_10y_3m": "float64",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MART_DIR = PROJECT_ROOT / "data" / "mart"
"""
### 1. 최초 적재
1. 아카이브 및 연월별 일드 커브 DataFrame 수집(완료 가정)
2. 수집한 DataFrame을 하나의 DataFrame으로 병합(완료 가정)
3. 날짜 기준 오름차순 정렬
4. 일드 스프레드 계산 및 별도 DataFrame 생성
5. 일드 커브 및 일드 스프레드 CSV 각각 저장
### 2. 증분 적재
1. 신규 연월 일드 커브 DataFrame 수집(완료 가정)
3. 일드 스프레드 계산 및 별도 DataFrame 생성
4. 기존 CSV를 DataFrame으로 변환
5. 기존 데이터에서 신규 수집 대상 연월과 이전 전체 데이터 분리
6. 기존 연월 데이터와 신규 수집 데이터 비교
7. 중복 날짜가 존재하는 경우 신규 수집 데이터 기준으로 갱신
8. 이전 전체 데이터와 갱신된 연월 데이터를 병합
9. 날짜 기준 오름차순 정렬
10. 일드 커브 및 일드 스프레드 CSV 각각 갱신
"""


# 가정: 전체 수집이 완료된 DataFrame이 입력으로 들어온다고 가정
def initialize_csv(df: pd.DataFrame) -> None:
    """통합된 DataFrame을 기반으로 초기 CSV를 적재한다.

    전체 기간의 Yield Curve DataFrame을 받아
    Yield Curve 와 Yield Spread CSV를 생성한다.
    """
    curve_df = df.sort_values(by="date")

    spread_df = _create_yield_curve_dataframe(curve_df)

    _save_curve_csv(curve_df)

    _save_spread_csv(spread_df)


# 가정: 전체 수집이 완료된 DataFrame이 입력으로 들어온다고 가정
def update_csv(df: pd.DataFrame) -> None:
    """신규 DataFrame을 기존 CSV에 반영한다.

    연월별 Yield Curve DataFrame과 기존 CSV를 기반으로
    신규 데이터를 Yield Curve 및 Yield Spread CSV에 증분한다.
    """


def _create_yield_curve_dataframe(curve_df: pd.DataFrame) -> pd.DataFrame:
    """Yield curve DataFrame을 사용해 Yield spread DataFrame을 생성한다."""
    return pd.DataFrame(
        {
            "date": curve_df["date"],
            "spread_10y_2y": curve_df["yield_10y"] - curve_df["yield_2y"],
            "spread_10y_3m": curve_df["yield_10y"] - curve_df["yield_3m"],
        },
        index=curve_df.index,
    )


def _save_curve_csv(curve_df: pd.DataFrame) -> None:
    """Yield curve DataFrame을 data/mart/yield_curve/yield_curve.csv에 저장한다."""

    save_path = MART_DIR / "yield_curve" / "yield_curve.csv"

    save_path.mkdir(parents=True, exist_ok=True)

    curve_df.to_csv(save_path, index=False)


def _save_spread_csv(spread_df: pd.DataFrame) -> None:
    """Yield spread DataFrame을 data/mart/yield_spread/yield_spread.csv에 저장한다."""

    save_path = MART_DIR / "yield_spread" / "yield_spread.csv"

    save_path.mkdir(parents=True, exist_ok=True)

    spread_df.to_csv(save_path, index=False)
