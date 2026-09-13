from alignment_check.compare.id_sets import compare_id_sets
from alignment_check.sequence import Sequence


def test_compare_id_sets_mixed() -> None:
    sequences_a = [
        Sequence(id="a", seq="ACGT"),
        Sequence(id="b", seq="ACGT"),
        Sequence(id="c", seq="ACGT"),
    ]
    sequences_b = [
        Sequence(id="b", seq="ACGT"),
        Sequence(id="c", seq="ACGT"),
        Sequence(id="d", seq="ACGT"),
    ]
    result = compare_id_sets(sequences_a, sequences_b)
    assert result["only_in_a"] == ["a"]
    assert result["only_in_b"] == ["d"]
    assert result["common_ids"] == ["b", "c"]
    assert result["num_only_in_a"] == 1
    assert result["num_only_in_b"] == 1
    assert result["num_common"] == 2


def test_compare_id_sets_identical() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = compare_id_sets(sequences, sequences)
    assert result["only_in_a"] == []
    assert result["only_in_b"] == []
    assert result["common_ids"] == ["a", "b"]
