from visualize import create_spread_chart


def test_figure_contains_spreads(spread_df):
    figure = create_spread_chart(spread_df)

    assert [trace.name for trace in figure.data] == [
        "T10Y2Y",
        "T10Y3M",
    ]


def test_figure_contains_zero_line(spread_df):
    figure = create_spread_chart(spread_df)

    assert any(
        shape.type == "line" and shape.y0 == 0 and shape.y1 == 0
        for shape in figure.layout.shapes
    )
