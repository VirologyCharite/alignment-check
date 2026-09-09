from alignment_check.info.site_gaps_plot import render_site_gaps_plot


def test_render_site_gaps_plot() -> None:
    html = render_site_gaps_plot({"fractions": [0.0, 0.5, 1.0]})
    assert "<div" in html
