"""Renders the site-homogeneity data (see `site_homogeneity.py`) as a
plot.
"""

from alignment_check.plotting import render_site_track_html


def render_site_homogeneity_plot(
    data: dict[str, object], include_plotlyjs: bool | str = False
) -> str:
    """Render the per-site homogeneity score as an HTML/JavaScript plot.

    Args:
        data: The return value of
            `site_homogeneity.compute_site_homogeneity`.
        include_plotlyjs: See `plotting.render_site_track_html`.

    Returns:
        An HTML fragment holding the plot.
    """
    return render_site_track_html(
        values=data["homogeneity"],
        y_title="Homogeneity (1=uniform, 0=maximally mixed)",
        title="Site homogeneity",
        include_plotlyjs=include_plotlyjs,
    )
