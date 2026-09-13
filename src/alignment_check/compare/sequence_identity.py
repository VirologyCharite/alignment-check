"""Checks whether common sequences actually have the same (ungapped)
content in both alignments.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def _ungapped_upper(seq: str, gap_chars: str) -> str:
    gap_set = set(gap_chars)
    return "".join(c.upper() for c in seq if c not in gap_set)


def compare_common_sequence_identity(
    sequences_a: list[Sequence],
    sequences_b: list[Sequence],
    common_ids: list[str],
    gap_chars: str = DEFAULT_GAP_CHARS,
) -> dict[str, object]:
    """Flag common IDs whose ungapped sequence differs between A and B.

    The comparison is case-insensitive. Only IDs in `common_ids` are
    checked.

    Args:
        sequences_a: Sequences from the first alignment.
        sequences_b: Sequences from the second alignment.
        common_ids: IDs to compare (e.g. from
            `id_sets.compare_id_sets`'s "common_ids").
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "mismatched_ids": IDs whose ungapped sequence
        differs between A and B, sorted.
    """
    common_set = set(common_ids)
    ungapped_a = {
        s.id: _ungapped_upper(s.seq, gap_chars)
        for s in sequences_a
        if s.id in common_set
    }
    ungapped_b = {
        s.id: _ungapped_upper(s.seq, gap_chars)
        for s in sequences_b
        if s.id in common_set
    }
    mismatched_ids = sorted(
        id_ for id_ in common_ids if ungapped_a.get(id_) != ungapped_b.get(id_)
    )
    return {"mismatched_ids": mismatched_ids}
