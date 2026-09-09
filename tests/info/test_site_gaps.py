from alignment_check.info.site_gaps import compute_site_gap_fractions
from alignment_check.sequence import Sequence


def test_compute_site_gap_fractions() -> None:
    sequences = [
        Sequence(id="a", seq="A-CG"),
        Sequence(id="b", seq="A-C-"),
    ]
    result = compute_site_gap_fractions(sequences)
    assert result["fractions"] == [0.0, 1.0, 0.0, 0.5]


def test_compute_site_gap_fractions_empty_alignment() -> None:
    assert compute_site_gap_fractions([]) == {"fractions": []}
