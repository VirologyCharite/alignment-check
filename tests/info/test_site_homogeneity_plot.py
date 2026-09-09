from alignment_check.info.site_homogeneity_plot import (
    render_site_homogeneity_plot,
)


def test_render_site_homogeneity_plot() -> None:
    html = render_site_homogeneity_plot({"homogeneity": [1.0, 0.0, None]})
    assert "<div" in html
