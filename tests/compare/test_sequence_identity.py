from alignment_check.compare.sequence_identity import (
    compare_common_sequence_identity,
)
from alignment_check.sequence import Sequence


def test_compare_common_sequence_identity_flags_mismatch() -> None:
    sequences_a = [Sequence(id="a", seq="AC-GT"), Sequence(id="b", seq="ACGT")]
    sequences_b = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = compare_common_sequence_identity(
        sequences_a, sequences_b, ["a", "b"]
    )
    assert result["mismatched_ids"] == ["b"]


def test_compare_common_sequence_identity_is_case_insensitive() -> None:
    sequences_a = [Sequence(id="a", seq="acgt")]
    sequences_b = [Sequence(id="a", seq="ACGT")]
    result = compare_common_sequence_identity(sequences_a, sequences_b, ["a"])
    assert result["mismatched_ids"] == []


def test_compare_common_sequence_identity_ignores_gaps() -> None:
    sequences_a = [Sequence(id="a", seq="A--CGT")]
    sequences_b = [Sequence(id="a", seq="ACG--T")]
    result = compare_common_sequence_identity(sequences_a, sequences_b, ["a"])
    assert result["mismatched_ids"] == []
