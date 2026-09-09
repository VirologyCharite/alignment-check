import math

from alignment_check.info.site_homogeneity import compute_site_homogeneity
from alignment_check.sequence import Sequence


def test_compute_site_homogeneity_fully_homogeneous() -> None:
    sequences = [Sequence(id="a", seq="A"), Sequence(id="b", seq="A")]
    result = compute_site_homogeneity(sequences)
    assert result["homogeneity"] == [1.0]


def test_compute_site_homogeneity_maximally_mixed() -> None:
    # Evenly split between two characters -> entropy is maximal -> 0.0.
    sequences = [Sequence(id="a", seq="A"), Sequence(id="b", seq="C")]
    result = compute_site_homogeneity(sequences)
    assert math.isclose(result["homogeneity"][0], 0.0, abs_tol=1e-9)


def test_compute_site_homogeneity_partially_mixed_is_between() -> None:
    sequences = [
        Sequence(id="a", seq="A"),
        Sequence(id="b", seq="A"),
        Sequence(id="c", seq="A"),
        Sequence(id="d", seq="C"),
    ]
    result = compute_site_homogeneity(sequences)
    assert 0.0 < result["homogeneity"][0] < 1.0


def test_compute_site_homogeneity_gap_only_site_is_none() -> None:
    sequences = [Sequence(id="a", seq="-"), Sequence(id="b", seq="-")]
    result = compute_site_homogeneity(sequences)
    assert result["homogeneity"] == [None]
