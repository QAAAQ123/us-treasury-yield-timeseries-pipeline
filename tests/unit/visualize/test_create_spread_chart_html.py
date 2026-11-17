from visualize import create_spread_chart_html


def test_chart_html_contains_spreads(spread_df):
    chart_html = create_spread_chart_html(spread_df)

    assert '"name":"T10Y2Y"' in chart_html
    assert '"name":"T10Y3M"' in chart_html


def test_chart_html_contains_zero_line(spread_df):
    chart_html = create_spread_chart_html(spread_df)

    assert '"type":"line"' in chart_html
    assert '"y0":0' in chart_html
    assert '"y1":0' in chart_html
