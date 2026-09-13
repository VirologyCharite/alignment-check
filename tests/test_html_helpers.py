from alignment_check.html_helpers import (
    escape,
    render_badge,
    render_check_item,
    render_page,
    render_table,
)


def test_escape_escapes_html() -> None:
    assert escape("<b>") == "&lt;b&gt;"


def test_render_badge() -> None:
    assert 'class="badge fail"' in render_badge(True)
    assert 'class="badge pass"' in render_badge(False)


def test_render_check_item_with_and_without_detail() -> None:
    with_detail = render_check_item(
        {"failed": True, "summary": "oops", "detail_html": "x, y"}
    )
    assert "oops" in with_detail
    assert '<div class="detail">x, y</div>' in with_detail

    without_detail = render_check_item({"failed": False, "summary": "ok"})
    assert "ok" in without_detail
    assert "detail" not in without_detail


def test_render_table_basic() -> None:
    html = render_table(["id", "gc"], [["a", 0.5]])
    assert "<th" in html
    assert "<td>a</td>" in html


def test_render_page_wraps_body() -> None:
    html = render_page("My Title", "My Heading", "<p>body</p>")
    assert "<title>My Title</title>" in html
    assert "<h1>My Heading</h1>" in html
    assert "<p>body</p>" in html
    assert "<!doctype html>" in html
