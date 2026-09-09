"""Renders the site-gap-fraction data (see `site_gaps.py`) as a plot."""

from alignment_check.plotting import render_site_track_html


def render_site_gaps_plot(
    data: dict[str, object], include_plotlyjs: bool | str = False
) -> str:
    """Render the per-site gap fraction as an HTML/JavaScript plot.

    Args:
        data: The return value of `site_gaps.compute_site_gap_fractions`.
        include_plotlyjs: See `plotting.render_site_track_html`.

    Returns:
        An HTML fragment holding the plot.
    """
    return render_site_track_html(
        values=data["fractions"],
        y_title="Fraction of sequences with a gap",
        title="Site gap fraction",
        include_plotlyjs=include_plotlyjs,
    )
