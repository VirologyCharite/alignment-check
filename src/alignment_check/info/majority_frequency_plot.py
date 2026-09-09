"""Renders the majority-frequency data (see `majority_frequency.py`) as a
plot.
"""

from alignment_check.plotting import render_site_track_html


def render_majority_frequency_plot(
    data: dict[str, object], include_plotlyjs: bool | str = False
) -> str:
    """Render the per-site majority frequency as an HTML/JavaScript plot.

    Args:
        data: The return value of
            `majority_frequency.compute_majority_frequencies`.
        include_plotlyjs: See `plotting.render_site_track_html`.

    Returns:
        An HTML fragment holding the plot.
    """
    return render_site_track_html(
        values=data["frequencies"],
        y_title="Majority-character frequency",
        title="Site majority-character frequency",
        include_plotlyjs=include_plotlyjs,
    )
