from alignment_check.checks.duplicate_ids import check_duplicate_ids
from alignment_check.sequence import Sequence


def test_check_duplicate_ids_flags_repeats() -> None:
    sequences = [
        Sequence(id="a", seq="ACGT"),
        Sequence(id="b", seq="ACGA"),
        Sequence(id="a", seq="ACGG"),
    ]
    result = check_duplicate_ids(sequences)
    assert result["duplicate_ids"] == ["a"]


def test_check_duplicate_ids_passes_unique_ids() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = check_duplicate_ids(sequences)
    assert result["duplicate_ids"] == []
