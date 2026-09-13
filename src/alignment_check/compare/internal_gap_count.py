"""Per-sequence "internal" gap count: gaps strictly between a sequence's
first and last residue, ignoring any leading/trailing gap run.

Leading and trailing gaps are often just padding added so every sequence
in a file has the same width (driven by other, longer/differently-placed
sequences), rather than something about how *this* sequence was aligned.
Counting only internal gaps avoids that noise when comparing two
alignments of the same sequences.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def compute_internal_gap_count(
    aligned_seq: str, gap_chars: str = DEFAULT_GAP_CHARS
) -> int:
    """Count gap characters strictly between the first and last residue.

    Args:
        aligned_seq: One sequence's aligned string.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        The number of gap characters found between the first and last
        non-gap character (inclusive of that range). 0 for an all-gap
        sequence.
    """
    gap_set = set(gap_chars)
    first = last = None
    for i, c in enumerate(aligned_seq):
        if c not in gap_set:
            if first is None:
                first = i
            last = i
    if first is None:
        return 0
    return sum(1 for c in aligned_seq[first : last + 1] if c in gap_set)


def compare_internal_gap_counts(
    sequences_a: list[Sequence],
    sequences_b: list[Sequence],
    common_ids: list[str],
    gap_chars: str = DEFAULT_GAP_CHARS,
) -> dict[str, object]:
    """Compute the internal gap count for each common sequence, in both.

    Args:
        sequences_a: Sequences from the first alignment.
        sequences_b: Sequences from the second alignment.
        common_ids: IDs to compare (e.g. from
            `id_sets.compare_id_sets`'s "common_ids").
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "counts_a" and "counts_b": each maps a common ID to
        its internal gap count in that alignment.
    """
    by_id_a = {s.id: s.seq for s in sequences_a}
    by_id_b = {s.id: s.seq for s in sequences_b}
    return {
        "counts_a": {
            id_: compute_internal_gap_count(by_id_a[id_], gap_chars)
            for id_ in common_ids
        },
        "counts_b": {
            id_: compute_internal_gap_count(by_id_b[id_], gap_chars)
            for id_ in common_ids
        },
    }
