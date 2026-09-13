from alignment_check.compare.id_order import compare_common_id_order
from alignment_check.sequence import Sequence


def test_compare_common_id_order_matches() -> None:
    sequences_a = [Sequence(id="a", seq=""), Sequence(id="b", seq="")]
    sequences_b = [Sequence(id="a", seq=""), Sequence(id="b", seq="")]
    result = compare_common_id_order(sequences_a, sequences_b, ["a", "b"])
    assert result["order_matches"] is True


def test_compare_common_id_order_mismatch() -> None:
    sequences_a = [Sequence(id="a", seq=""), Sequence(id="b", seq="")]
    sequences_b = [Sequence(id="b", seq=""), Sequence(id="a", seq="")]
    result = compare_common_id_order(sequences_a, sequences_b, ["a", "b"])
    assert result["order_matches"] is False


def test_compare_common_id_order_ignores_non_common_ids() -> None:
    sequences_a = [
        Sequence(id="a", seq=""),
        Sequence(id="only_a", seq=""),
        Sequence(id="b", seq=""),
    ]
    sequences_b = [
        Sequence(id="a", seq=""),
        Sequence(id="b", seq=""),
        Sequence(id="only_b", seq=""),
    ]
    result = compare_common_id_order(sequences_a, sequences_b, ["a", "b"])
    assert result["order_matches"] is True
