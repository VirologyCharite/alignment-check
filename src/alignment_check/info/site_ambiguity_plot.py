"""Renders the site-ambiguity data (see `site_ambiguity.py`) as a plot."""

from alignment_check.plotting import render_site_track_html


def render_site_ambiguity_plot(
    data: dict[str, object], include_plotlyjs: bool | str = False
) -> str:
    """Render the per-site ambiguity score as an HTML/JavaScript plot.

    Args:
        data: The return value of
            `site_ambiguity.compute_site_ambiguity`.
        include_plotlyjs: See `plotting.render_site_track_html`.

    Returns:
        An HTML fragment holding the plot.
    """
    return render_site_track_html(
        values=data["scores"],
        y_title="Mean IUPAC degeneracy (1=unambiguous, 4=N)",
        title="Site nucleotide ambiguity",
        include_plotlyjs=include_plotlyjs,
    )
