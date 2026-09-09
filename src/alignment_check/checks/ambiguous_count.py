"""Anomaly check: sequences with a suspiciously high number of ambiguous
nucleotide codes.

Meaningful only for nucleotide alignments; a caller working with a
protein alignment should skip this check. 'N' is excluded here since it
has its own check (`n_count`).
"""

from alignment_check.alphabet import NUCLEOTIDE_AMBIGUITY_DEGENERACY
from alignment_check.outliers import OutlierResult, detect_outliers
from alignment_check.sequence import Sequence

AMBIGUOUS_CODES_EXCLUDING_N = frozenset(NUCLEOTIDE_AMBIGUITY_DEGENERACY) - {"N"}


def compute_ambiguous_counts(sequences: list[Sequence]) -> dict[str, int]:
    """Count each sequence's ambiguous nucleotide codes, excluding 'N'.

    Args:
        sequences: The sequences to measure.

    Returns:
        Maps each sequence ID to its count of R/Y/S/W/K/M/B/D/H/V
        characters (case-insensitive).
    """
    return {
        s.id: sum(1 for c in s.seq if c.upper() in AMBIGUOUS_CODES_EXCLUDING_N)
        for s in sequences
    }


def check_ambiguous_count(
    sequences: list[Sequence],
    low_threshold: float | None = None,
    high_threshold: float | None = None,
) -> dict[str, object]:
    """Flag sequences with a suspiciously high ambiguous-code count.

    Args:
        sequences: The sequences to check.
        low_threshold: A fixed lower threshold; statistical if None.
        high_threshold: A fixed upper threshold; statistical if None.

    Returns:
        A dict with "values" (see `compute_ambiguous_counts`) and
        "outliers" (an `OutlierResult`).
    """
    values = compute_ambiguous_counts(sequences)
    outliers: OutlierResult = detect_outliers(values, low_threshold, high_threshold)
    return {"values": values, "outliers": outliers}
