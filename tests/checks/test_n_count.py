from alignment_check.checks.n_count import check_n_count, compute_n_counts
from alignment_check.sequence import Sequence


def test_compute_n_counts_is_case_insensitive() -> None:
    result = compute_n_counts([Sequence(id="a", seq="ACnNGT")])
    assert result == {"a": 2}


def test_check_n_count_flags_outlier_with_fixed_threshold() -> None:
    sequences = [
        Sequence(id="a", seq="ACGT"),  # 0 Ns
        Sequence(id="b", seq="NNNN"),  # 4 Ns
    ]
    result = check_n_count(sequences, low_threshold=-1, high_threshold=1)
    assert result["outliers"].low_ids == []
    assert result["outliers"].high_ids == ["b"]


def test_check_n_count_passes_uniform_sequences() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = check_n_count(sequences)
    assert result["outliers"].high_ids == []
