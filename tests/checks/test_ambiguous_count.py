from alignment_check.checks.ambiguous_count import (
    check_ambiguous_count,
    compute_ambiguous_counts,
)
from alignment_check.sequence import Sequence


def test_compute_ambiguous_counts_excludes_n() -> None:
    result = compute_ambiguous_counts([Sequence(id="a", seq="ACRYN")])
    assert result == {"a": 2}


def test_check_ambiguous_count_flags_outlier_with_fixed_threshold() -> None:
    sequences = [
        Sequence(id="a", seq="ACGT"),  # 0 ambiguous
        Sequence(id="b", seq="RYSW"),  # 4 ambiguous
    ]
    result = check_ambiguous_count(sequences, low_threshold=-1, high_threshold=1)
    assert result["outliers"].high_ids == ["b"]


def test_check_ambiguous_count_passes_uniform_sequences() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = check_ambiguous_count(sequences)
    assert result["outliers"].high_ids == []
