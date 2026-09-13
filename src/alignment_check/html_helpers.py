"""Low-level HTML building blocks shared by `report.py` (single-alignment
reports) and `compare/compare_report.py` (two-alignment comparison
reports), so both look and behave consistently.
"""

import html as html_module

STYLE = """
:root { color-scheme: light; }
body {
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    background: #f6f7f9;
    color: #1a1d21;
    margin: 0;
    padding: 2rem;
}
h1 { margin-top: 0; }
.container { max-width: 960px; margin: 0 auto; }
section {
    background: #fff;
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
section > h2 {
    margin-top: 0;
    border-bottom: 1px solid #e1e4e8;
    padding-bottom: 0.5rem;
}
.item { padding: 0.6rem 0; border-bottom: 1px solid #f0f1f3; }
.item:last-child { border-bottom: none; }
.badge {
    display: inline-block;
    min-width: 4.5rem;
    text-align: center;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.6rem;
}
.badge.pass { background: #d9f2e3; color: #1c7a3f; }
.badge.fail { background: #fbdcdc; color: #a4262c; }
.detail { color: #555; font-size: 0.9rem; margin: 0.3rem 0 0 5.3rem; }
table { border-collapse: collapse; width: 100%; margin-top: 0.5rem; }
th, td { text-align: left; padding: 0.4rem 0.8rem; border-bottom: 1px solid #f0f1f3; }
th { cursor: pointer; user-select: none; background: #fafbfc; }
th.sortable::after { content: " \\2195"; color: #999; }
.plot { margin-bottom: 2rem; }
.note {
    color: #7a5c00; background: #fff8e1; border-radius: 6px;
    padding: 0.75rem 1rem;
}
"""

SORT_SCRIPT = """
function sortTable(table, columnIndex) {
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);
    const ascending = table.dataset.sortColumn == columnIndex
        && table.dataset.sortDirection === "asc" ? false : true;
    rows.sort((a, b) => {
        const x = a.cells[columnIndex].textContent.trim();
        const y = b.cells[columnIndex].textContent.trim();
        const xNum = parseFloat(x);
        const yNum = parseFloat(y);
        const cmp = (!isNaN(xNum) && !isNaN(yNum))
            ? xNum - yNum
            : x.localeCompare(y);
        return ascending ? cmp : -cmp;
    });
    rows.forEach((row) => tbody.appendChild(row));
    table.dataset.sortColumn = columnIndex;
    table.dataset.sortDirection = ascending ? "asc" : "desc";
}
"""


def escape(value: object) -> str:
    """HTML-escape a value's string representation."""
    return html_module.escape(str(value))


def render_badge(failed: bool) -> str:
    """Render a PASS/FAIL badge span."""
    return (
        '<span class="badge fail">FAIL</span>'
        if failed
        else '<span class="badge pass">PASS</span>'
    )


def render_check_item(item: dict[str, object]) -> str:
    """Render one {"failed", "summary", "detail_html"} item as a row.

    Args:
        item: A dict with "failed" (bool), "summary" (str), and
            optionally "detail_html" (a pre-built, already-escaped-where-
            needed HTML fragment).

    Returns:
        An HTML fragment for one item.
    """
    failed = bool(item["failed"])
    detail_html = item.get("detail_html") or ""
    detail = f'<div class="detail">{detail_html}</div>' if detail_html else ""
    return (
        f'<div class="item">{render_badge(failed)}'
        f'{escape(item["summary"])}{detail}</div>'
    )


def render_table(headers: list[str], rows: list[list[object]]) -> str:
    """Render a sortable HTML table.

    Args:
        headers: Column headers.
        rows: Table rows; each must have the same length as `headers`.

    Returns:
        An HTML `<table>` string with click-to-sort column headers.
    """
    header_html = "".join(
        f'<th class="sortable" onclick="sortTable(this.closest(\'table\'), {i})">'
        f"{escape(h)}</th>"
        for i, h in enumerate(headers)
    )
    body_html = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        f"<table><thead><tr>{header_html}</tr></thead>"
        f"<tbody>{body_html}</tbody></table>"
    )


def render_page(title: str, heading: str, body_html: str) -> str:
    """Wrap a body fragment in a complete, self-contained HTML document.

    Args:
        title: The page `<title>`.
        heading: The `<h1>` shown at the top of the page.
        body_html: The already-built HTML to place inside the page's
            container div.

    Returns:
        A complete HTML document as a string.
    """
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f"<title>{escape(title)}</title>"
        f"<style>{STYLE}</style>"
        f"<script>{SORT_SCRIPT}</script>"
        "</head><body><div class='container'>"
        f"<h1>{escape(heading)}</h1>"
        f"{body_html}"
        "</div></body></html>"
    )
