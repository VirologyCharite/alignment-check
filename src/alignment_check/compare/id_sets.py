"""Compares the sequence ID sets of two alignments."""

from alignment_check.sequence import Sequence


def compare_id_sets(
    sequences_a: list[Sequence], sequences_b: list[Sequence]
) -> dict[str, object]:
    """Find which sequence IDs are shared, and which are unique to one side.

    Args:
        sequences_a: Sequences from the first alignment.
        sequences_b: Sequences from the second alignment.

    Returns:
        A dict with:
            "only_in_a": IDs present in A but not B, in A's order.
            "only_in_b": IDs present in B but not A, in B's order.
            "common_ids": IDs present in both, in A's order.
            "num_only_in_a", "num_only_in_b", "num_common": their counts.
    """
    ids_a = [s.id for s in sequences_a]
    ids_b = [s.id for s in sequences_b]
    set_a = set(ids_a)
    set_b = set(ids_b)

    only_in_a = [id_ for id_ in ids_a if id_ not in set_b]
    only_in_b = [id_ for id_ in ids_b if id_ not in set_a]
    common_ids = [id_ for id_ in ids_a if id_ in set_b]

    return {
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "common_ids": common_ids,
        "num_only_in_a": len(only_in_a),
        "num_only_in_b": len(only_in_b),
        "num_common": len(common_ids),
    }
