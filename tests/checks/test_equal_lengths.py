from alignment_check.checks.equal_lengths import check_equal_lengths
from alignment_check.sequence import Sequence


def test_check_equal_lengths_passes_when_consistent() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = check_equal_lengths(sequences)
    assert result["consistent"] is True
    assert result["unique_lengths"] == [4]
    assert result["lengths"] == {"a": 4, "b": 4}


def test_check_equal_lengths_flags_mismatch() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACG")]
    result = check_equal_lengths(sequences)
    assert result["consistent"] is False
    assert result["unique_lengths"] == [3, 4]
    assert result["lengths"] == {"a": 4, "b": 3}


def test_check_equal_lengths_empty_alignment_is_consistent() -> None:
    result = check_equal_lengths([])
    assert result["consistent"] is True
    assert result["unique_lengths"] == []
