from visualize import VISIBLE_CURVE, create_curve_chart_html


def test_chart_html_is_plotly_html(curve_df):
    chart_html = create_curve_chart_html(curve_df)

    assert isinstance(chart_html, str)
    assert "<html" in chart_html.lower()
    assert "plotly" in chart_html.lower()


def test_chart_html_sets_default_visibility(curve_df):
    chart_html = create_curve_chart_html(curve_df)

    # 기본 표시 만기를 제외한 나머지 만기는 legendonly로 숨김 처리된다
    hidden_count = len(curve_df.columns) - 1 - len(VISIBLE_CURVE)

    assert chart_html.count('"visible":"legendonly"') == hidden_count
