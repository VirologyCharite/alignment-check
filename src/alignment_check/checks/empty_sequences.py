"""Error check: sequences that are all gaps or all 'N' characters.

Sequences flagged by this check carry no usable information, so callers
should exclude them from every other check, anomaly, and plot.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def check_empty_sequences(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Flag sequences that are entirely gaps, or entirely 'N' characters.

    Args:
        sequences: The sequences read from the input file.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with:
            "all_gap_ids": IDs of sequences with no non-gap characters.
            "all_n_ids": IDs of sequences whose only non-gap character
                is 'N' (case-insensitive).
            "flagged_ids": The union of the above, sorted.
    """
    gap_set = set(gap_chars)
    all_gap_ids = []
    all_n_ids = []
    for s in sequences:
        non_gap = [c for c in s.seq if c not in gap_set]
        if not non_gap:
            all_gap_ids.append(s.id)
        elif all(c.upper() == "N" for c in non_gap):
            all_n_ids.append(s.id)

    return {
        "all_gap_ids": all_gap_ids,
        "all_n_ids": all_n_ids,
        "flagged_ids": sorted(all_gap_ids + all_n_ids),
    }
