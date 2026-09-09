from alignment_check.info.site_ambiguity import compute_site_ambiguity
from alignment_check.sequence import Sequence


def test_compute_site_ambiguity_mixed_degeneracies() -> None:
    # Site 0: A (1), R (2), N (4) -> mean = 7/3.
    sequences = [
        Sequence(id="a", seq="A"),
        Sequence(id="b", seq="R"),
        Sequence(id="c", seq="N"),
    ]
    result = compute_site_ambiguity(sequences)
    assert result["scores"] == [7 / 3]


def test_compute_site_ambiguity_all_unambiguous() -> None:
    sequences = [Sequence(id="a", seq="A"), Sequence(id="b", seq="C")]
    result = compute_site_ambiguity(sequences)
    assert result["scores"] == [1.0]


def test_compute_site_ambiguity_gap_only_site_is_none() -> None:
    sequences = [Sequence(id="a", seq="-"), Sequence(id="b", seq="-")]
    result = compute_site_ambiguity(sequences)
    assert result["scores"] == [None]
