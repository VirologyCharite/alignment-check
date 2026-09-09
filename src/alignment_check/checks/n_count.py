"""Anomaly check: sequences with a suspiciously high number of 'N'
characters.
"""

from alignment_check.outliers import OutlierResult, detect_outliers
from alignment_check.sequence import Sequence


def compute_n_counts(sequences: list[Sequence]) -> dict[str, int]:
    """Count each sequence's 'N' characters (case-insensitive).

    Args:
        sequences: The sequences to measure.

    Returns:
        Maps each sequence ID to its 'N' count.
    """
    return {s.id: sum(1 for c in s.seq if c.upper() == "N") for s in sequences}


def check_n_count(
    sequences: list[Sequence],
    low_threshold: float | None = None,
    high_threshold: float | None = None,
) -> dict[str, object]:
    """Flag sequences with a suspiciously low or high 'N' count.

    Args:
        sequences: The sequences to check.
        low_threshold: A fixed lower threshold; statistical if None.
        high_threshold: A fixed upper threshold; statistical if None.

    Returns:
        A dict with "values" (see `compute_n_counts`) and "outliers"
        (an `OutlierResult`).
    """
    values = compute_n_counts(sequences)
    outliers: OutlierResult = detect_outliers(values, low_threshold, high_threshold)
    return {"values": values, "outliers": outliers}
