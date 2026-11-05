"""
미국 국채 Yield Curve 및 Yield Spread 데이터 파이프라인

Treasury XML 원본 데이터를 수집하고 정제하여 CSV에 초기 및 증분 적재한다.
적재된 CSV 데이터를 기반으로 Yield Curve 및 Yield Spread 시각화 HTML을 생성한다.

주요 기능:
- 초기 데이터 수집 및 CSV 적재
- 월별 신규 데이터 수집 및 CSV 증분 적재
- 최신 CSV 데이터를 활용한 시각화 HTML 생성
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd

from extract import fetch_yield_curve_archive_xml, fetch_yield_curve_xml
from load_csv import CURVE_PATH, SPREAD_PATH, YIELD_DTYPES, initialize_csv, update_csv
from logger_config import logger
from missing_data import handle_missing_data
from transform import create_yield_curve_dataframe, parse_yield_curve_records
from visualize import (
    CURVE_HTML_PATH,
    SPREAD_HTML_PATH,
    create_curve_chart,
    create_spread_chart,
    save_to_html,
)

TODAY = datetime.now(ZoneInfo("America/New_York")).date()


def run_initial_pipeline() -> None:
    """전체 데이터를 수집하여 초기 CSV를 적재한다."""
    archive_curve_records: list[dict[str, date | str | None]] = (
        parse_yield_curve_records(fetch_yield_curve_archive_xml(1990, 2023))
    )

    current_year = TODAY.year
    years_to_fetch = list(range(2024, current_year + 1))
    yearly_curve_records: list[dict[str, date | str | None]] = []

    for year in years_to_fetch:
        year_records = parse_yield_curve_records(fetch_yield_curve_xml(year))
        yearly_curve_records.extend(year_records)

    initial_records = archive_curve_records + yearly_curve_records
    logger.info("초기 데이터 레코드 생성 완료: %s건", len(initial_records))

    initial_records = handle_missing_data(initial_records)

    initial_dataframe = create_yield_curve_dataframe(initial_records)
    logger.info("초기 데이터 DataFrame 생성 완료: %s행", len(initial_dataframe))

    initialize_csv(initial_dataframe)


def run_incremental_pipeline() -> None:
    """신규 데이터를 수집하여 CSV를 증분 적재한다."""
    current_year = TODAY.year
    current_month = TODAY.month

    curve_records: list[dict[str, date | str | None]] = parse_yield_curve_records(
        fetch_yield_curve_xml(current_year, current_month)
    )
    if not curve_records:
        logger.info("신규 데이터가 없어 증분 적재를 건너뜁니다.")
        return
    logger.info("신규 데이터 레코드 생성 완료: %s건", len(curve_records))

    upsert_records = handle_missing_data(curve_records)

    upsert_dataframe = create_yield_curve_dataframe(upsert_records)
    logger.info("신규 데이터 DataFrame 생성 완료: %s행", len(upsert_dataframe))

    update_csv(upsert_dataframe)


def generate_visualizations():
    """최신 CSV 데이터를 기반으로 Yield Curve 및 Spread HTML을 생성한다."""

    curve_df = pd.read_csv(CURVE_PATH, parse_dates=["date"], dtype=YIELD_DTYPES)
    spread_df = pd.read_csv(
        SPREAD_PATH,
        parse_dates=["date"],
        dtype={
            "spread_10y_2y": "float64",
            "spread_10y_3m": "float64",
        },
    )
    logger.info(
        "시각화용 DataFrame 생성 완료: Curve %s행, Spread %s행",
        len(curve_df),
        len(spread_df),
    )

    curve_figure = create_curve_chart(curve_df)
    spread_figure = create_spread_chart(spread_df)

    logger.info("Yield Curve/Spread Figure 생성 완료")

    save_to_html(curve_figure, CURVE_HTML_PATH)
    save_to_html(spread_figure, SPREAD_HTML_PATH)
