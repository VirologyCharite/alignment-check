from alignment_check.info.pairwise_identity_histogram_plot import (
    render_pairwise_identity_histogram_plot,
)


def test_render_pairwise_identity_histogram_plot() -> None:
    html = render_pairwise_identity_histogram_plot(
        {"identities": [0.9, 0.95, 1.0], "pairs_compared": 3, "pairs_skipped": 0}
    )
    assert "<div" in html
