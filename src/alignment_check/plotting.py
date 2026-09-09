"""Shared Plotly rendering helpers used by the `*_plot.py` modules.

Each `*_plot.py` module still owns its own public render function (per
check/info item, one piece of functionality per file); this module just
factors out the boilerplate for building the common "one line per site,
across the whole alignment" figure shape they all share.
"""

import plotly.graph_objects as go


def render_site_track_html(
    values: list[float | None],
    y_title: str,
    title: str,
    include_plotlyjs: bool | str = False,
) -> str:
    """Render a per-site line plot as a standalone HTML/JavaScript string.

    Args:
        values: One value per alignment site (1-based on the resulting
            plot's x-axis). None marks a site with no defined value
            (e.g. a gap-only column) and is left as a gap in the line.
        y_title: The y-axis label.
        title: The plot title.
        include_plotlyjs: Passed through to `Figure.to_html`; True embeds
            the full plotly.js library (only do this once per report),
            False assumes it is already present on the page.

    Returns:
        An HTML fragment (a <div> plus, if requested, the plotly.js
        library) that renders the plot when placed in a web page.
    """
    sites = list(range(1, len(values) + 1))
    figure = go.Figure(
        data=go.Scatter(x=sites, y=values, mode="lines", line={"width": 1})
    )
    figure.update_layout(
        title=title,
        xaxis_title="Alignment site",
        yaxis_title=y_title,
        template="plotly_white",
        height=350,
        margin={"l": 60, "r": 20, "t": 40, "b": 40},
    )
    return figure.to_html(full_html=False, include_plotlyjs=include_plotlyjs)
