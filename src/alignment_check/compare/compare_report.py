"""Assembles the gathered comparison results into one self-contained HTML
report.
"""

from alignment_check.html_helpers import (
    escape,
    render_badge,
    render_check_item,
    render_page,
    render_table,
)


def render_compare_report(results: dict[str, object]) -> str:
    """Render the gathered comparison results as a complete HTML page.

    Args:
        results: A dict with:
            "name_a", "name_b": Names of the two inputs, for display.
            "load_error": None on success, otherwise {"message": str}.
            "info_lines": Plain informational strings (sequence counts,
                widths, etc.) shown above the checks.
            "tier1_items": A list of {"failed", "summary", "detail_html"}
                dicts, one per basic-comparison check.
            "tier2_note": None, or a string explaining why the more
                detailed gap-pattern comparison was skipped.
            "gap_count_table": {"headers": [...], "rows": [[...]]} or
                None.
            "plots": A list of {"title", "html"} dicts.

    Returns:
        A complete HTML document as a string.
    """
    title = f"Alignment comparison: {results['name_a']} vs {results['name_b']}"

    load_error = results.get("load_error")
    if load_error is not None:
        body = (
            "<section><h2>Errors</h2>"
            f'<div class="item">{render_badge(True)}'
            f'{escape(load_error["message"])}</div></section>'
        )
        return render_page(title, title, body)

    parts = ["<section><h2>Basic comparison tests</h2>"]
    for line in results.get("info_lines", []):
        parts.append(f"<p>{escape(line)}</p>")
    parts.append(
        "".join(render_check_item(item) for item in results["tier1_items"])
    )
    parts.append("</section>")

    tier2_note = results.get("tier2_note")
    if tier2_note:
        parts.append(f'<p class="note">{escape(tier2_note)}</p>')

    gap_count_table = results.get("gap_count_table")
    if gap_count_table is not None:
        parts.append("<section><h2>Internal gap counts (common sequences)</h2>")
        parts.append(render_table(gap_count_table["headers"], gap_count_table["rows"]))
        parts.append("</section>")

    plots = results.get("plots", [])
    if plots:
        parts.append("<section><h2>Gap-pattern comparison</h2>")
        for plot in plots:
            parts.append(f'<div class="plot"><h3>{escape(plot["title"])}</h3>')
            parts.append(plot["html"])
            parts.append("</div>")
        parts.append("</section>")

    return render_page(title, title, "".join(parts))
