"""Renders the internal gap count comparison (see
`internal_gap_count.py`) as a scatter plot.
"""

import plotly.graph_objects as go


def render_gap_count_scatter_plot(
    data: dict[str, object], include_plotlyjs: bool | str = False
) -> str:
    """Render internal gap count, A vs B, one point per common sequence.

    Args:
        data: The return value of
            `internal_gap_count.compare_internal_gap_counts`.
        include_plotlyjs: Passed through to `Figure.to_html`; True embeds
            the full plotly.js library (only do this once per report),
            False assumes it is already present on the page.

    Returns:
        An HTML fragment holding the plot.
    """
    counts_a = data["counts_a"]
    counts_b = data["counts_b"]
    ids = list(counts_a)
    xs = [counts_a[id_] for id_ in ids]
    ys = [counts_b[id_] for id_ in ids]

    figure = go.Figure()
    max_value = max(xs + ys, default=0) + 1
    figure.add_trace(
        go.Scatter(
            x=[0, max_value],
            y=[0, max_value],
            mode="lines",
            line={"dash": "dot", "color": "gray"},
            name="A = B",
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            text=ids,
            hovertemplate="%{text}<br>A: %{x}<br>B: %{y}<extra></extra>",
            marker={"size": 9},
            name="sequences",
        )
    )
    figure.update_layout(
        title="Internal gap count per sequence",
        xaxis_title="Gap count in A",
        yaxis_title="Gap count in B",
        template="plotly_white",
        height=450,
        showlegend=False,
        margin={"l": 60, "r": 20, "t": 40, "b": 40},
    )
    return figure.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
