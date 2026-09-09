"""Error check: the alignment contains zero sequences."""

from alignment_check.sequence import Sequence


def check_empty_alignment(sequences: list[Sequence]) -> dict[str, object]:
    """Flag an alignment that contains no sequences at all.

    Args:
        sequences: The sequences read from the input file.

    Returns:
        A dict with "empty" (bool) and "count" (the number of sequences).
    """
    return {"empty": len(sequences) == 0, "count": len(sequences)}
