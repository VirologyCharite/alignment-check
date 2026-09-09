"""Anomaly check: sequences with a suspiciously low or high gap count (or,
equivalently, ungapped length).
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.outliers import OutlierResult, detect_outliers
from alignment_check.sequence import Sequence


def compute_gap_counts(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, dict[str, int]]:
    """Compute each sequence's gap count and ungapped length.

    Args:
        sequences: The sequences to measure.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        Maps each sequence ID to a dict with "gap_count" and
        "ungapped_length".
    """
    gap_set = set(gap_chars)
    result = {}
    for s in sequences:
        gap_count = sum(1 for c in s.seq if c in gap_set)
        result[s.id] = {
            "gap_count": gap_count,
            "ungapped_length": len(s.seq) - gap_count,
        }
    return result


def check_gap_count(
    sequences: list[Sequence],
    gap_chars: str = DEFAULT_GAP_CHARS,
    low_threshold: float | None = None,
    high_threshold: float | None = None,
) -> dict[str, object]:
    """Flag sequences with a suspiciously low or high gap count.

    Args:
        sequences: The sequences to check.
        gap_chars: Characters treated as alignment gaps.
        low_threshold: A fixed lower threshold; statistical if None.
        high_threshold: A fixed upper threshold; statistical if None.

    Returns:
        A dict with "counts" (see `compute_gap_counts`) and "outliers"
        (an `OutlierResult`, based on gap count).
    """
    counts = compute_gap_counts(sequences, gap_chars)
    values = {id_: v["gap_count"] for id_, v in counts.items()}
    outliers: OutlierResult = detect_outliers(values, low_threshold, high_threshold)
    return {"counts": counts, "outliers": outliers}
