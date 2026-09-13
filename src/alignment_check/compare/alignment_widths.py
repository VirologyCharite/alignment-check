"""Compares the overall column count (width) of two alignments."""

from alignment_check.checks.equal_lengths import check_equal_lengths
from alignment_check.sequence import Sequence


def compare_alignment_widths(
    sequences_a: list[Sequence], sequences_b: list[Sequence]
) -> dict[str, object]:
    """Report each alignment's width(s).

    Args:
        sequences_a: Sequences from the first alignment.
        sequences_b: Sequences from the second alignment.

    Returns:
        A dict with "widths_a" and "widths_b": the distinct sequence
        lengths in each alignment, sorted (usually a single value each;
        more than one means that alignment's own sequences aren't all
        the same length).
    """
    return {
        "widths_a": check_equal_lengths(sequences_a)["unique_lengths"],
        "widths_b": check_equal_lengths(sequences_b)["unique_lengths"],
    }
