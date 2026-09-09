"""Info: per-site majority-character frequency.

At each site, this is the fraction of sequences (among those without a
gap there) that carry the most common character. E.g. a site with 5
A's, 2 C's, and 3 G's has a majority frequency of 0.5. This is not a
consensus sequence: no single character is chosen for the site, only
the fraction of the largest group.

Gap characters are excluded from both the counts and the denominator
(gap prevalence is reported separately by `site_gaps.py`). Requires all
sequences to be the same length; callers should skip this when
`equal_lengths.check_equal_lengths` reports "consistent": False.
"""

from collections import Counter

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def compute_majority_frequencies(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Compute the majority-character frequency at each site.

    Args:
        sequences: The (equal-length) sequences to measure.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "frequencies": one value per site, in site order.
        A gap-only site is reported as None (undefined).
    """
    if not sequences:
        return {"frequencies": []}

    gap_set = set(gap_chars)
    length = len(sequences[0].seq)
    frequencies: list[float | None] = []
    for col in range(length):
        counts = Counter(
            s.seq[col].upper() for s in sequences if s.seq[col] not in gap_set
        )
        if counts:
            frequencies.append(max(counts.values()) / counts.total())
        else:
            frequencies.append(None)
    return {"frequencies": frequencies}
