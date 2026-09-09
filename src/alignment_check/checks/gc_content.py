"""Anomaly check: sequences with a suspiciously low or high G/C content.

Meaningful for nucleotide sequences; a caller working with a protein
alignment should skip this check.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.outliers import OutlierResult, detect_outliers
from alignment_check.sequence import Sequence


def compute_gc_content(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, float]:
    """Compute each sequence's G/C fraction, ignoring gap characters.

    Args:
        sequences: The sequences to measure.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        Maps each sequence ID to its G/C fraction (0.0-1.0). A sequence
        with no non-gap characters is omitted.
    """
    gap_set = set(gap_chars)
    values = {}
    for s in sequences:
        non_gap = [c.upper() for c in s.seq if c not in gap_set]
        if non_gap:
            gc_count = sum(1 for c in non_gap if c in "GC")
            values[s.id] = gc_count / len(non_gap)
    return values


def check_gc_content(
    sequences: list[Sequence],
    gap_chars: str = DEFAULT_GAP_CHARS,
    low_threshold: float | None = None,
    high_threshold: float | None = None,
) -> dict[str, object]:
    """Flag sequences with suspiciously low or high G/C content.

    Args:
        sequences: The sequences to check.
        gap_chars: Characters treated as alignment gaps.
        low_threshold: A fixed lower threshold; statistical if None.
        high_threshold: A fixed upper threshold; statistical if None.

    Returns:
        A dict with "values" (see `compute_gc_content`) and "outliers"
        (an `OutlierResult`).
    """
    values = compute_gc_content(sequences, gap_chars)
    outliers: OutlierResult = detect_outliers(values, low_threshold, high_threshold)
    return {"values": values, "outliers": outliers}
