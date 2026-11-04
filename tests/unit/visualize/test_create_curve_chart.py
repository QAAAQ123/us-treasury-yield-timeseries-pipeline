from visualize import create_curve_chart


def test_figure_sets_default_visibility(curve_df):
    figure = create_curve_chart(curve_df)

    visible_traces = [
        trace.name
        for trace in figure.data
        if trace.visible is True or trace.visible is None
    ]

    assert visible_traces == ["3M", "2Y", "10Y"]
