from alignment_check.compare.internal_gap_count import (
    compare_internal_gap_counts,
    compute_internal_gap_count,
)
from alignment_check.sequence import Sequence


def test_compute_internal_gap_count_ignores_leading_and_trailing() -> None:
    assert compute_internal_gap_count("--AC--GT--") == 2


def test_compute_internal_gap_count_no_gaps() -> None:
    assert compute_internal_gap_count("ACGT") == 0


def test_compute_internal_gap_count_all_gaps() -> None:
    assert compute_internal_gap_count("----") == 0


def test_compare_internal_gap_counts() -> None:
    sequences_a = [
        Sequence(id="a", seq="--AC--GT--"),  # internal: 2
        Sequence(id="b", seq="ACGT"),  # internal: 0
    ]
    sequences_b = [
        Sequence(id="a", seq="ACGT----"),  # internal: 0 (trailing only)
        Sequence(id="b", seq="AC--GT"),  # internal: 2
    ]
    result = compare_internal_gap_counts(sequences_a, sequences_b, ["a", "b"])
    assert result["counts_a"] == {"a": 2, "b": 0}
    assert result["counts_b"] == {"a": 0, "b": 2}
