from alignment_check.info.pairwise_identity_histogram import (
    compute_pairwise_identity_histogram,
)
from alignment_check.sequence import Sequence


def test_compute_pairwise_identity_histogram() -> None:
    sequences = [
        Sequence(id="a", seq="ACGT"),
        Sequence(id="b", seq="ACGT"),
        Sequence(id="c", seq="ACGA"),
    ]
    result = compute_pairwise_identity_histogram(sequences)
    assert sorted(result["identities"]) == [0.75, 0.75, 1.0]
    assert result["pairs_compared"] == 3
    assert result["pairs_skipped"] == 0


def test_compute_pairwise_identity_histogram_skips_uncomparable_pairs() -> None:
    sequences = [Sequence(id="a", seq="--"), Sequence(id="b", seq="--")]
    result = compute_pairwise_identity_histogram(sequences)
    assert result["identities"] == []
    assert result["pairs_compared"] == 0
    assert result["pairs_skipped"] == 1


def test_compute_pairwise_identity_histogram_custom_identity_fn() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = compute_pairwise_identity_histogram(
        sequences, identity_fn=lambda a, b, gap_chars: 0.42
    )
    assert result["identities"] == [0.42]
