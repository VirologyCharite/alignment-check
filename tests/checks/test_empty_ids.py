from alignment_check.checks.empty_ids import check_empty_ids
from alignment_check.sequence import Sequence


def test_check_empty_ids_flags_empty_id() -> None:
    sequences = [
        Sequence(id="a", seq="ACGT"),
        Sequence(id="", seq="ACGA"),
    ]
    result = check_empty_ids(sequences)
    assert result["indices"] == [1]


def test_check_empty_ids_passes_when_all_present() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = check_empty_ids(sequences)
    assert result["indices"] == []
