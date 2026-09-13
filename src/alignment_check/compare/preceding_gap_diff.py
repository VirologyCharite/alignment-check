"""Per-residue difference in how many gaps precede that residue, between
two alignments of the same sequence.

Requires the two aligned strings to have identical ungapped content
(same residues, same order) -- callers should only call this for IDs
that passed `sequence_identity.compare_common_sequence_identity`.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def compute_preceding_gap_counts(
    aligned_seq: str, gap_chars: str = DEFAULT_GAP_CHARS
) -> list[int]:
    """For each residue, count the gap characters that precede it.

    Args:
        aligned_seq: One sequence's aligned string.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        One value per residue (in residue order): the number of gap
        characters in `aligned_seq` before that residue's column.
    """
    gap_set = set(gap_chars)
    counts = []
    gap_count = 0
    for c in aligned_seq:
        if c in gap_set:
            gap_count += 1
        else:
            counts.append(gap_count)
    return counts


def compute_preceding_gap_diff(
    seq_a: str, seq_b: str, gap_chars: str = DEFAULT_GAP_CHARS
) -> list[int]:
    """Compute the baseline-adjusted per-residue preceding-gap difference.

    The count of leading gaps (before the first residue) is subtracted
    out of each alignment's curve first, so the result reflects only
    internal placement differences and always starts at 0 -- otherwise a
    difference in each alignment's unrelated leading-gap padding would
    shift the whole curve up or down.

    Args:
        seq_a: The sequence's aligned string in alignment A.
        seq_b: The same sequence's aligned string in alignment B. Must
            have the same ungapped content as `seq_a`.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        One value per residue: (gaps preceding it in A, relative to A's
        own leading gaps) minus (the same, for B).
    """
    preceding_a = compute_preceding_gap_counts(seq_a, gap_chars)
    preceding_b = compute_preceding_gap_counts(seq_b, gap_chars)
    if not preceding_a:
        return []
    baseline_a = preceding_a[0]
    baseline_b = preceding_b[0]
    return [
        (a - baseline_a) - (b - baseline_b)
        for a, b in zip(preceding_a, preceding_b)
    ]


def compare_preceding_gap_diffs(
    sequences_a: list[Sequence],
    sequences_b: list[Sequence],
    common_ids: list[str],
    gap_chars: str = DEFAULT_GAP_CHARS,
) -> dict[str, object]:
    """Compute the preceding-gap diff curve for each common sequence.

    Args:
        sequences_a: Sequences from the first alignment.
        sequences_b: Sequences from the second alignment.
        common_ids: IDs to compute this for (should be restricted to
            IDs whose ungapped content matches in both alignments).
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "diffs": maps each ID to its diff curve (see
        `compute_preceding_gap_diff`).
    """
    by_id_a = {s.id: s.seq for s in sequences_a}
    by_id_b = {s.id: s.seq for s in sequences_b}
    return {
        "diffs": {
            id_: compute_preceding_gap_diff(by_id_a[id_], by_id_b[id_], gap_chars)
            for id_ in common_ids
        }
    }
