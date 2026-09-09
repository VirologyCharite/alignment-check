from alignment_check.checks.gap_count import check_gap_count, compute_gap_counts
from alignment_check.sequence import Sequence


def test_compute_gap_counts() -> None:
    result = compute_gap_counts([Sequence(id="a", seq="AC--GT")])
    assert result == {"a": {"gap_count": 2, "ungapped_length": 4}}


def test_check_gap_count_flags_outlier_with_fixed_threshold() -> None:
    sequences = [
        Sequence(id="a", seq="ACGT"),  # 0 gaps
        Sequence(id="b", seq="----"),  # 4 gaps
    ]
    result = check_gap_count(sequences, low_threshold=1, high_threshold=3)
    assert result["outliers"].low_ids == ["a"]
    assert result["outliers"].high_ids == ["b"]


def test_check_gap_count_passes_uniform_sequences() -> None:
    sequences = [Sequence(id="a", seq="AC-T"), Sequence(id="b", seq="AC-A")]
    result = check_gap_count(sequences)
    assert result["outliers"].low_ids == []
    assert result["outliers"].high_ids == []
