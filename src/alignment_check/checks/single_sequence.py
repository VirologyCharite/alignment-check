"""Error check: the alignment contains only a single sequence."""

from alignment_check.sequence import Sequence


def check_single_sequence(sequences: list[Sequence]) -> dict[str, object]:
    """Flag an alignment that contains exactly one sequence.

    Most of the other checks and plots (site identity, gap fraction,
    pairwise identity, and so on) are not meaningful with only one
    sequence.

    Args:
        sequences: The sequences read from the input file.

    Returns:
        A dict with "single" (bool) and "count" (the number of
        sequences).
    """
    return {"single": len(sequences) == 1, "count": len(sequences)}
