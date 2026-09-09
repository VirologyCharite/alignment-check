from alignment_check.checks.gap_only_columns import check_gap_only_columns
from alignment_check.sequence import Sequence


def test_check_gap_only_columns_flags_a_gap_only_column() -> None:
    sequences = [
        Sequence(id="a", seq="A-CG"),
        Sequence(id="b", seq="A-CT"),
    ]
    result = check_gap_only_columns(sequences)
    assert result["columns"] == [1]
    assert result["count"] == 1


def test_check_gap_only_columns_passes_when_none_are_gap_only() -> None:
    sequences = [
        Sequence(id="a", seq="ACGT"),
        Sequence(id="b", seq="A-CT"),
    ]
    result = check_gap_only_columns(sequences)
    assert result["columns"] == []


def test_check_gap_only_columns_empty_alignment() -> None:
    result = check_gap_only_columns([])
    assert result["columns"] == []
