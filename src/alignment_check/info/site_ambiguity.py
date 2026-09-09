"""Info: per-site nucleotide ambiguity score.

Nucleotide alignments only. Each non-gap character at a site scores its
IUPAC degeneracy: an unambiguous base (A/C/G/T/U) scores 1, a two-fold
ambiguity code (e.g. R, Y) scores 2, a three-fold code (e.g. B, D)
scores 3, and 'N' scores 4. The site's value is the mean of these
scores over its non-gap characters.

Requires all sequences to be the same length; callers should skip this
when `equal_lengths.check_equal_lengths` reports "consistent": False.
"""

from alignment_check.alphabet import (
    DEFAULT_GAP_CHARS,
    NUCLEOTIDE_AMBIGUITY_DEGENERACY,
    NUCLEOTIDE_BASES,
)
from alignment_check.sequence import Sequence

DEGENERACY = {base: 1 for base in NUCLEOTIDE_BASES} | NUCLEOTIDE_AMBIGUITY_DEGENERACY


def compute_site_ambiguity(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Compute the mean nucleotide ambiguity score at each site.

    Args:
        sequences: The (equal-length, nucleotide) sequences to measure.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "scores": one mean degeneracy score per site, in
        site order. A site with no scorable (non-gap, recognized
        nucleotide) characters is reported as None.
    """
    if not sequences:
        return {"scores": []}

    gap_set = set(gap_chars)
    length = len(sequences[0].seq)
    scores: list[float | None] = []
    for col in range(length):
        degeneracies = [
            DEGENERACY[s.seq[col].upper()]
            for s in sequences
            if s.seq[col] not in gap_set and s.seq[col].upper() in DEGENERACY
        ]
        scores.append(sum(degeneracies) / len(degeneracies) if degeneracies else None)
    return {"scores": scores}
