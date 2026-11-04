import plotly.graph_objects as go

from visualize import save_to_html


def test_figure_creates_html_file(tmp_path):
    figure = go.Figure()
    output_path = tmp_path / "test_path" / "test.html"

    save_to_html(figure, output_path)

    assert output_path.is_file()
    assert output_path.stat().st_size > 0
