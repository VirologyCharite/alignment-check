from alignment_check.compare.alignment_widths import compare_alignment_widths
from alignment_check.sequence import Sequence


def test_compare_alignment_widths_different() -> None:
    sequences_a = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGT")]
    sequences_b = [Sequence(id="a", seq="ACGTAC"), Sequence(id="b", seq="ACGTAC")]
    result = compare_alignment_widths(sequences_a, sequences_b)
    assert result == {"widths_a": [4], "widths_b": [6]}


def test_compare_alignment_widths_inconsistent_within_one_file() -> None:
    sequences_a = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACG")]
    sequences_b = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGT")]
    result = compare_alignment_widths(sequences_a, sequences_b)
    assert result == {"widths_a": [3, 4], "widths_b": [4]}
