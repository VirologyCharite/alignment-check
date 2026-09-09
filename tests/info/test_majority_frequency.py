from alignment_check.info.majority_frequency import compute_majority_frequencies
from alignment_check.sequence import Sequence


def test_compute_majority_frequencies() -> None:
    # Site 0: 5 As, 2 Cs, 3 Gs -> majority frequency 0.5.
    sequences = (
        [Sequence(id=f"a{i}", seq="A") for i in range(5)]
        + [Sequence(id=f"c{i}", seq="C") for i in range(2)]
        + [Sequence(id=f"g{i}", seq="G") for i in range(3)]
    )
    result = compute_majority_frequencies(sequences)
    assert result["frequencies"] == [0.5]


def test_compute_majority_frequencies_gap_only_site_is_none() -> None:
    sequences = [Sequence(id="a", seq="-"), Sequence(id="b", seq="-")]
    result = compute_majority_frequencies(sequences)
    assert result["frequencies"] == [None]


def test_compute_majority_frequencies_ignores_gaps_in_denominator() -> None:
    sequences = [
        Sequence(id="a", seq="A"),
        Sequence(id="b", seq="A"),
        Sequence(id="c", seq="-"),
    ]
    result = compute_majority_frequencies(sequences)
    assert result["frequencies"] == [1.0]
