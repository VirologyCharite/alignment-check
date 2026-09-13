from alignment_check.compare.files_identical import compare_files_identical
from alignment_check.sequence import Sequence


def test_compare_files_identical_true() -> None:
    sequences = [Sequence(id="a", seq="AC-GT"), Sequence(id="b", seq="ACGGT")]
    result = compare_files_identical(sequences, list(sequences))
    assert result["identical"] is True


def test_compare_files_identical_false_different_gaps() -> None:
    sequences_a = [Sequence(id="a", seq="AC-GT")]
    sequences_b = [Sequence(id="a", seq="ACG-T")]
    result = compare_files_identical(sequences_a, sequences_b)
    assert result["identical"] is False


def test_compare_files_identical_false_different_order() -> None:
    sequences_a = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    sequences_b = [Sequence(id="b", seq="ACGA"), Sequence(id="a", seq="ACGT")]
    result = compare_files_identical(sequences_a, sequences_b)
    assert result["identical"] is False
