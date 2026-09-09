"""Anomaly check: columns/sites that are entirely gaps.

Requires all sequences to be the same length; callers should skip this
when `equal_lengths.check_equal_lengths` reports "consistent": False.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def check_gap_only_columns(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Flag alignment columns where every sequence has a gap.

    Args:
        sequences: The (equal-length) sequences to check.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "columns" (the 0-based indices of gap-only columns)
        and "count".
    """
    if not sequences:
        return {"columns": [], "count": 0}

    gap_set = set(gap_chars)
    length = len(sequences[0].seq)
    columns = [
        col
        for col in range(length)
        if all(s.seq[col] in gap_set for s in sequences)
    ]
    return {"columns": columns, "count": len(columns)}
