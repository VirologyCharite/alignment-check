from alignment_check.compare.preceding_gap_diff_plot import (
    render_preceding_gap_diff_plot,
)


def test_render_preceding_gap_diff_plot() -> None:
    data = {"diffs": {"a": [0, 0, -1, -1], "b": [0, 1, 1, 0]}}
    html = render_preceding_gap_diff_plot(data)
    assert "<div" in html
