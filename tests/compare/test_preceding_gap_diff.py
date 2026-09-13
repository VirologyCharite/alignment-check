from alignment_check.compare.preceding_gap_diff import (
    compare_preceding_gap_diffs,
    compute_preceding_gap_counts,
    compute_preceding_gap_diff,
)
from alignment_check.sequence import Sequence


def test_compute_preceding_gap_counts() -> None:
    assert compute_preceding_gap_counts("--AC-GT") == [2, 2, 3, 3]


def test_compute_preceding_gap_counts_no_gaps() -> None:
    assert compute_preceding_gap_counts("ACGT") == [0, 0, 0, 0]


def test_compute_preceding_gap_diff_baseline_adjusted() -> None:
    # seq_a has 2 leading gaps then an internal gap; seq_b has no leading
    # gaps but 2 internal gaps -- same ungapped content "ACGT".
    diff = compute_preceding_gap_diff("--AC-GT", "AC--GT")
    assert diff == [0, 0, -1, -1]


def test_compute_preceding_gap_diff_identical_placement_is_zero() -> None:
    diff = compute_preceding_gap_diff("--ACGT", "--ACGT")
    assert diff == [0, 0, 0, 0]


def test_compare_preceding_gap_diffs() -> None:
    sequences_a = [Sequence(id="a", seq="--AC-GT")]
    sequences_b = [Sequence(id="a", seq="AC--GT")]
    result = compare_preceding_gap_diffs(sequences_a, sequences_b, ["a"])
    assert result["diffs"] == {"a": [0, 0, -1, -1]}
