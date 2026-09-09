"""Assembles the gathered check/info results into one self-contained HTML
report.

This module only knows how to render a generic shape of result (see
`render_html_report`); it has no per-check special cases, so it does not
need to change when the CLI script gains new checks or info functions.
"""

import html as html_module

_STYLE = """
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

_SORT_SCRIPT = """
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


def _escape(value: object) -> str:
    return html_module.escape(str(value))


def _render_badge(failed: bool) -> str:
    return (
        '<span class="badge fail">FAIL</span>'
        if failed
        else '<span class="badge pass">PASS</span>'
    )


def _render_check_item(item: dict[str, object]) -> str:
    failed = bool(item["failed"])
    detail_html = item.get("detail_html") or ""
    detail = f'<div class="detail">{detail_html}</div>' if detail_html else ""
    return (
        f'<div class="item">{_render_badge(failed)}'
        f'{_escape(item["summary"])}{detail}</div>'
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
        f"{_escape(h)}</th>"
        for i, h in enumerate(headers)
    )
    body_html = "".join(
        "<tr>" + "".join(f"<td>{_escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return (
        f"<table><thead><tr>{header_html}</tr></thead>"
        f"<tbody>{body_html}</tbody></table>"
    )


def render_html_report(results: dict[str, object]) -> str:
    """Render the gathered results as a complete, self-contained HTML page.

    Args:
        results: A dict with:
            "input_name": Name of the input, for display.
            "load_error": None on success, otherwise {"message": str}.
            "basic_facts": `basic_facts.compute_basic_facts`'s return
                value, or None if the input couldn't be loaded.
            "errors": A list of {"name", "failed", "summary",
                "detail_html"} dicts, one per error check that ran.
            "anomalies": Same shape as "errors", one per anomaly check.
            "per_sequence_summary": {"headers": [...], "rows": [[...]]}
                or None.
            "plots": A list of {"title", "html"} dicts.
            "notes": A list of informational strings (e.g. about
                sequences excluded from analysis).

    Returns:
        A complete HTML document as a string.
    """
    parts = ['<!doctype html><html><head><meta charset="utf-8">']
    parts.append(f"<title>Alignment check: {_escape(results['input_name'])}</title>")
    parts.append(f"<style>{_STYLE}</style>")
    parts.append(f"<script>{_SORT_SCRIPT}</script>")
    parts.append("</head><body><div class='container'>")
    parts.append(f"<h1>Alignment check: {_escape(results['input_name'])}</h1>")

    load_error = results.get("load_error")
    if load_error is not None:
        parts.append("<section><h2>Errors</h2>")
        parts.append(
            '<div class="item">'
            f'{_render_badge(True)}{_escape(load_error["message"])}</div>'
        )
        parts.append("</section></div></body></html>")
        return "".join(parts)

    for note in results.get("notes", []):
        parts.append(f'<p class="note">{_escape(note)}</p>')

    basic_facts = results.get("basic_facts")
    if basic_facts is not None:
        parts.append("<section><h2>General info</h2>")
        parts.append(f"<p>Number of sequences: {basic_facts['num_sequences']}</p>")
        lengths = basic_facts["lengths"]
        length_text = (
            str(lengths[0]) if len(lengths) == 1 else f"varies: {lengths}"
        )
        parts.append(f"<p>Sequence length: {_escape(length_text)}</p>")
        parts.append("</section>")

    parts.append("<section><h2>Errors</h2>")
    parts.append("".join(_render_check_item(item) for item in results["errors"]))
    parts.append("</section>")

    parts.append("<section><h2>Anomalies</h2>")
    parts.append("".join(_render_check_item(item) for item in results["anomalies"]))
    parts.append("</section>")

    summary = results.get("per_sequence_summary")
    if summary is not None:
        parts.append("<section><h2>Per-sequence summary</h2>")
        parts.append(render_table(summary["headers"], summary["rows"]))
        parts.append("</section>")

    plots = results.get("plots", [])
    if plots:
        parts.append("<section><h2>Info plots</h2>")
        for plot in plots:
            parts.append(f'<div class="plot"><h3>{_escape(plot["title"])}</h3>')
            parts.append(plot["html"])
            parts.append("</div>")
        parts.append("</section>")

    parts.append("</div></body></html>")
    return "".join(parts)
