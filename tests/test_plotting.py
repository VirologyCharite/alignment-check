from alignment_check.plotting import render_site_track_html


def test_render_site_track_html_without_plotlyjs() -> None:
    html = render_site_track_html([0.1, 0.2, None, 0.4], "Y", "Title")
    assert "<div" in html
    assert "plotly.js" not in html.lower()


def test_render_site_track_html_with_plotlyjs() -> None:
    html = render_site_track_html(
        [0.1, 0.2], "Y", "Title", include_plotlyjs=True
    )
    assert "<div" in html
    assert "<script" in html
