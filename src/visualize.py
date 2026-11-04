"""
미국 국채 Yield Curve 및 Yield Spread 시각화 모듈

정제된 DataFrame을 입력받아 Plotly Figure 객체를 생성한다
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from logger_config import logger

CURVE_LABELS = {
    "date": "Date",
    "yield_1m": "1M",
    "yield_1_5m": "1.5M",
    "yield_2m": "2M",
    "yield_3m": "3M",
    "yield_4m": "4M",
    "yield_6m": "6M",
    "yield_1y": "1Y",
    "yield_2y": "2Y",
    "yield_3y": "3Y",
    "yield_5y": "5Y",
    "yield_7y": "7Y",
    "yield_10y": "10Y",
    "yield_20y": "20Y",
    "yield_30y": "30Y",
}

SPREAD_LABELS = {
    "date": "Date",
    "spread_10y_2y": "T10Y2Y",
    "spread_10y_3m": "T10Y3M",
}

VISIBLE_CURVE = ["3M", "2Y", "10Y"]

SAVE_DIR = Path(__file__).resolve().parents[1] / "html"
CURVE_HTML_PATH = SAVE_DIR / "yield_curve" / "yield_curve.html"
SPREAD_HTML_PATH = SAVE_DIR / "yield_spread" / "yield_spread.html"


def create_curve_chart(df: pd.DataFrame) -> go.Figure:
    """Yield Curve 차트를 생성한다.

    전체 만기의 금리 데이터를 시각화하며, 기본적으로 3M, 2Y, 10Y
    금리만 표시하고 나머지 만기는 범례를 통해 선택할 수 있도록 한다

    Args:
        df: date 및 전체 만기의 Yield 컬럼을 포함하는 DataFrame

    Returns:
        Yield Curve를 표현하는 Plotly Figure 객체
    """
    chart_df = df.rename(columns=CURVE_LABELS)

    figure = px.line(
        chart_df,
        x="Date",
        y=[
            chart_label
            for df_label, chart_label in CURVE_LABELS.items()
            if df_label.startswith("yield_")
        ],
        title="US Treasury Yield Curve",
        labels={
            "Date": "Date",
            "value": "Yield(%)",
            "variable": "Maturity",
        },
    )

    figure.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend_title="Maturity",
    )

    figure.for_each_trace(
        lambda trace: (
            trace.update(visible=True)
            if trace.name in VISIBLE_CURVE
            else trace.update(visible="legendonly")
        )
    )

    figure.update_xaxes(rangeslider_visible=True)

    logger.info(
        "Yield Curve 차트 생성 완료 | 기간: %s ~ %s | 데이터: %d건",
        df["date"].min(),
        df["date"].max(),
        len(df),
    )

    return figure


def create_spread_chart(df: pd.DataFrame) -> go.Figure:
    """Yield Spread 차트를 생성한다.

    10년물과 2년물, 3개월물 금리 간 스프레드를 시각화하며,
    양수와 음수를 구분할 수 있도록 0 기준선을 표시한다

    Args:
        df: date, spread_10y_2y, spread_10y_3m 컬럼을 포함하는 DataFrame

    Returns:
        Yield Spread를 표현하는 Plotly Figure 객체
    """
    chart_df = df.rename(columns=SPREAD_LABELS)

    figure = px.line(
        chart_df,
        x="Date",
        y=[
            chart_label
            for df_label, chart_label in SPREAD_LABELS.items()
            if df_label.startswith("spread_")
        ],
        title="US Treasury Yield Spread",
        labels={
            "Date": "Date",
            "value": "Spread(%p)",
            "variable": "Spread",
        },
    )

    figure.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend_title="Spread",
    )

    figure.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        line_width=1,
    )

    figure.update_xaxes(rangeslider_visible=True)

    logger.info(
        "Yield Spread 차트 생성 완료 | 기간: %s ~ %s | 데이터: %d건",
        df["date"].min(),
        df["date"].max(),
        len(df),
    )

    return figure


def save_to_html(figure: go.Figure, output_path: Path) -> None:
    """Plotly Figure를 HTML 파일로 저장한다.

    Args:
        figure: HTML로 저장할 Plotly Figure 객체
        output_path: HTML 파일 저장 경로
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(output_path)

    logger.info("차트 HTML 저장 완료: %s", output_path)
