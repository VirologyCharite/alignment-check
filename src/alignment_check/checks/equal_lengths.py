"""Error check: not all sequences are the same length."""

from alignment_check.sequence import Sequence


def check_equal_lengths(sequences: list[Sequence]) -> dict[str, object]:
    """Flag an alignment whose sequences are not all the same length.

    Site-based checks and plots (which compare a single column across
    all sequences) require every sequence to be the same length, so
    callers should skip those when this check reports "consistent":
    False.

    Args:
        sequences: The sequences read from the input file.

    Returns:
        A dict with:
            "consistent": True if all sequences have the same length.
            "lengths": Maps each sequence ID to its length.
            "unique_lengths": The distinct lengths present, sorted.
    """
    lengths = {s.id: len(s.seq) for s in sequences}
    unique_lengths = sorted(set(lengths.values()))
    return {
        "consistent": len(unique_lengths) <= 1,
        "lengths": lengths,
        "unique_lengths": unique_lengths,
    }
