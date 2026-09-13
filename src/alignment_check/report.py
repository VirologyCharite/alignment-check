"""Assembles the gathered check/info results into one self-contained HTML
report.

This module only knows how to render a generic shape of result (see
`render_html_report`); it has no per-check special cases, so it does not
need to change when the CLI script gains new checks or info functions.
"""

from alignment_check.html_helpers import (
    escape,
    render_badge,
    render_check_item,
    render_page,
    render_table,
)

__all__ = ["render_html_report", "render_table"]


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
    title = f"Alignment check: {results['input_name']}"

    load_error = results.get("load_error")
    if load_error is not None:
        body = (
            "<section><h2>Errors</h2>"
            f'<div class="item">{render_badge(True)}'
            f'{escape(load_error["message"])}</div></section>'
        )
        return render_page(title, title, body)

    parts = []
    for note in results.get("notes", []):
        parts.append(f'<p class="note">{escape(note)}</p>')

    basic_facts = results.get("basic_facts")
    if basic_facts is not None:
        parts.append("<section><h2>General info</h2>")
        parts.append(f"<p>Number of sequences: {basic_facts['num_sequences']}</p>")
        lengths = basic_facts["lengths"]
        length_text = (
            str(lengths[0]) if len(lengths) == 1 else f"varies: {lengths}"
        )
        parts.append(f"<p>Sequence length: {escape(length_text)}</p>")
        parts.append("</section>")

    parts.append("<section><h2>Errors</h2>")
    parts.append("".join(render_check_item(item) for item in results["errors"]))
    parts.append("</section>")

    parts.append("<section><h2>Anomalies</h2>")
    parts.append("".join(render_check_item(item) for item in results["anomalies"]))
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
            parts.append(f'<div class="plot"><h3>{escape(plot["title"])}</h3>')
            parts.append(plot["html"])
            parts.append("</div>")
        parts.append("</section>")

    return render_page(title, title, "".join(parts))
