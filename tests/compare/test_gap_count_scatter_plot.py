from alignment_check.compare.gap_count_scatter_plot import (
    render_gap_count_scatter_plot,
)


def test_render_gap_count_scatter_plot() -> None:
    data = {"counts_a": {"a": 1, "b": 2}, "counts_b": {"a": 3, "b": 0}}
    html = render_gap_count_scatter_plot(data)
    assert "<div" in html
