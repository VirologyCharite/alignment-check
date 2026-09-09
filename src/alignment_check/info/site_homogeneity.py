"""Info: per-site homogeneity, i.e. how uniform vs. mixed each site is.

Unlike the majority-frequency score (which only looks at the size of
the largest group), homogeneity accounts for the site's whole
character distribution, via normalized Shannon entropy. A site with a
single character (ignoring gaps) scores 1.0 (fully homogeneous); a site
where the observed characters are evenly split scores 0.0 (maximally
mixed). Entropy is normalized against the number of distinct
characters actually observed at that site (not a fixed alphabet size).

Requires all sequences to be the same length; callers should skip this
when `equal_lengths.check_equal_lengths` reports "consistent": False.
"""

import math
from collections import Counter

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def compute_site_homogeneity(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Compute the homogeneity score at each site.

    Args:
        sequences: The (equal-length) sequences to measure.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "homogeneity": one score per site (1.0 = fully
        homogeneous, 0.0 = maximally mixed), in site order. A gap-only
        site is reported as None.
    """
    if not sequences:
        return {"homogeneity": []}

    gap_set = set(gap_chars)
    length = len(sequences[0].seq)
    homogeneity: list[float | None] = []
    for col in range(length):
        counts = Counter(
            s.seq[col].upper() for s in sequences if s.seq[col] not in gap_set
        )
        total = counts.total()
        if total == 0:
            homogeneity.append(None)
        elif len(counts) <= 1:
            homogeneity.append(1.0)
        else:
            entropy = -sum(
                (count / total) * math.log2(count / total)
                for count in counts.values()
            )
            max_entropy = math.log2(len(counts))
            homogeneity.append(1.0 - entropy / max_entropy)
    return {"homogeneity": homogeneity}
