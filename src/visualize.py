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
SPREAD_LABLES = {
    "date": "Date",
    "spread_10y_2y": "T10Y2Y",
    "spread_10y_3m": "T10Y3M",
}
VISIBLE_CURVE = ["3M", "2Y", "10Y"]


def create_curve_chart(df: pd.DataFrame) -> go.Figure:
    """Yield curve chart Figure를 생성한다.

    Args:
        df: 특정 기간의 Yield curve 데이터 프레임
    Returns:
        Yield curve를 그래프로 표현한 Figure 객체
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

    logger.info("Yield Curve 차트 생성 완료: %s까지", df.iloc[0]["date"])

    return figure


def create_spread_chart(df: pd.DataFrame) -> go.Figure:
    """Yield spread chart Figure를 생성한다.

    Args:
        df: 특정 기간의 Yield curve 데이터 프레임
    Returns:
        Yield spread를 그래프로 표현한 Figure 객체
    """
    chart_df = df.rename(columns=SPREAD_LABLES)

    figure = px.line(
        chart_df,
        x="Date",
        y=[
            chart_label
            for df_label, chart_label in SPREAD_LABLES.items()
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

    logger.info("Yield Spread 차트 생성 완료: %s까지", df.iloc[0]["date"])

    return figure
