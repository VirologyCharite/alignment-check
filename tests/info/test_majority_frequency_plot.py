from alignment_check.info.majority_frequency_plot import (
    render_majority_frequency_plot,
)


def test_render_majority_frequency_plot() -> None:
    html = render_majority_frequency_plot({"frequencies": [0.5, None, 1.0]})
    assert "<div" in html
