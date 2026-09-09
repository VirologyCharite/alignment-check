"""Info: site gap count/percentage across the alignment.

Requires all sequences to be the same length; callers should skip this
when `equal_lengths.check_equal_lengths` reports "consistent": False.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def compute_site_gap_fractions(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Compute the fraction of sequences with a gap at each site.

    Args:
        sequences: The (equal-length) sequences to measure.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "fractions": one gap fraction (0.0-1.0) per site, in
        site order.
    """
    if not sequences:
        return {"fractions": []}

    gap_set = set(gap_chars)
    length = len(sequences[0].seq)
    n = len(sequences)
    fractions = [
        sum(1 for s in sequences if s.seq[col] in gap_set) / n
        for col in range(length)
    ]
    return {"fractions": fractions}
