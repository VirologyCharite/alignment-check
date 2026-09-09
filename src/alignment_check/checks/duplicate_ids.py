"""Error check: duplicate sequence IDs."""

from collections import Counter

from alignment_check.sequence import Sequence


def check_duplicate_ids(sequences: list[Sequence]) -> dict[str, object]:
    """Flag sequence IDs that appear more than once.

    Args:
        sequences: The sequences read from the input file.

    Returns:
        A dict with "duplicate_ids": the IDs that appear more than
        once, sorted.
    """
    counts = Counter(s.id for s in sequences)
    duplicate_ids = sorted(id_ for id_, count in counts.items() if count > 1)
    return {"duplicate_ids": duplicate_ids}
