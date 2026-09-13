"""Renders the per-residue preceding-gap-count difference curves (see
`preceding_gap_diff.py`) as a multi-line plot, one line per sequence.
"""

import plotly.graph_objects as go


def render_preceding_gap_diff_plot(
    data: dict[str, object], include_plotlyjs: bool | str = False
) -> str:
    """Render each common sequence's preceding-gap-count diff curve.

    All sequences are drawn on one plot; click a legend entry to toggle
    that sequence's line on/off.

    Args:
        data: The return value of
            `preceding_gap_diff.compare_preceding_gap_diffs`.
        include_plotlyjs: Passed through to `Figure.to_html`; True embeds
            the full plotly.js library (only do this once per report),
            False assumes it is already present on the page.

    Returns:
        An HTML fragment holding the plot.
    """
    figure = go.Figure()
    for seq_id, values in data["diffs"].items():
        figure.add_trace(
            go.Scatter(
                x=list(range(1, len(values) + 1)),
                y=values,
                mode="lines",
                name=seq_id,
            )
        )
    figure.update_layout(
        title="Per-residue internal gap-count difference (A minus B)",
        xaxis_title="Residue position (ungapped)",
        yaxis_title="Gaps preceding this residue: A minus B",
        template="plotly_white",
        height=450,
        margin={"l": 60, "r": 20, "t": 40, "b": 40},
    )
    return figure.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
