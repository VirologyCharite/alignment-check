from alignment_check.checks.empty_alignment import check_empty_alignment
from alignment_check.sequence import Sequence


def test_check_empty_alignment_flags_zero_sequences() -> None:
    result = check_empty_alignment([])
    assert result["empty"] is True
    assert result["count"] == 0


def test_check_empty_alignment_passes_with_sequences() -> None:
    result = check_empty_alignment([Sequence(id="a", seq="ACGT")])
    assert result["empty"] is False
    assert result["count"] == 1
