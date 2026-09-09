"""The pairwise sequence identity calculation, as a swappable function.

Kept separate from `pairwise_identity_histogram.py` so alternative
identity definitions can be added later and selected (e.g. via a CLI
option) without changing the code that uses them.
"""

import math

from alignment_check.alphabet import DEFAULT_GAP_CHARS


def default_identity(
    seq_a: str, seq_b: str, gap_chars: str = DEFAULT_GAP_CHARS
) -> float:
    """Compute the identity between two aligned sequences.

    Columns where both sequences have a gap are ignored entirely (they
    contribute to neither the numerator nor the denominator). A column
    where exactly one sequence has a gap counts as a mismatch.

    Args:
        seq_a: The first sequence (must be the same length as `seq_b`).
        seq_b: The second sequence.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        The fraction of compared columns that matched, in [0.0, 1.0].
        NaN if there were no comparable (not both-gap) columns.
    """
    gap_set = set(gap_chars)
    compared = 0
    matches = 0
    for a, b in zip(seq_a, seq_b):
        a_gap = a in gap_set
        b_gap = b in gap_set
        if a_gap and b_gap:
            continue
        compared += 1
        if not a_gap and not b_gap and a.upper() == b.upper():
            matches += 1
    return matches / compared if compared else math.nan
