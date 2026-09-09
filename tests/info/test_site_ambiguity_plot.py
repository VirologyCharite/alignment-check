from alignment_check.info.site_ambiguity_plot import render_site_ambiguity_plot


def test_render_site_ambiguity_plot() -> None:
    html = render_site_ambiguity_plot({"scores": [1.0, 2.0, None]})
    assert "<div" in html
