"""Renders the pairwise-identity data (see `pairwise_identity_histogram.py`)
as a histogram.
"""

import plotly.graph_objects as go


def render_pairwise_identity_histogram_plot(
    data: dict[str, object], include_plotlyjs: bool | str = False
) -> str:
    """Render the pairwise identity distribution as an HTML/JavaScript plot.

    Args:
        data: The return value of
            `pairwise_identity_histogram.compute_pairwise_identity_histogram`.
        include_plotlyjs: Passed through to `Figure.to_html`; True embeds
            the full plotly.js library (only do this once per report),
            False assumes it is already present on the page.

    Returns:
        An HTML fragment holding the plot.
    """
    figure = go.Figure(data=go.Histogram(x=data["identities"]))
    figure.update_layout(
        title="Pairwise sequence identity",
        xaxis_title="Identity",
        yaxis_title="Number of sequence pairs",
        template="plotly_white",
        height=350,
        margin={"l": 60, "r": 20, "t": 40, "b": 40},
    )
    return figure.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
