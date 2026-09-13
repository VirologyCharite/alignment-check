"""Checks whether the common sequence IDs appear in the same relative
order in both alignments.
"""

from alignment_check.sequence import Sequence


def compare_common_id_order(
    sequences_a: list[Sequence],
    sequences_b: list[Sequence],
    common_ids: list[str],
) -> dict[str, object]:
    """Check whether the common IDs' relative order matches in A and B.

    IDs that aren't in `common_ids` are ignored, so this is meaningful
    even when the two alignments don't contain exactly the same
    sequences.

    Args:
        sequences_a: Sequences from the first alignment.
        sequences_b: Sequences from the second alignment.
        common_ids: IDs to compare the order of (e.g. from
            `id_sets.compare_id_sets`'s "common_ids").

    Returns:
        A dict with "order_matches": True if the common IDs appear in
        the same relative order in both alignments.
    """
    common_set = set(common_ids)
    order_a = [s.id for s in sequences_a if s.id in common_set]
    order_b = [s.id for s in sequences_b if s.id in common_set]
    return {"order_matches": order_a == order_b}
