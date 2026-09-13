"""Checks whether two alignments are exactly identical."""

from alignment_check.sequence import Sequence


def compare_files_identical(
    sequences_a: list[Sequence], sequences_b: list[Sequence]
) -> dict[str, object]:
    """Check whether the two alignments are exactly identical.

    Identical means the same number of sequences, in the same order,
    with the same ID and exact (including gaps) sequence content at
    each position.

    Args:
        sequences_a: Sequences from the first alignment.
        sequences_b: Sequences from the second alignment.

    Returns:
        A dict with "identical": bool.
    """
    pairs_a = [(s.id, s.seq) for s in sequences_a]
    pairs_b = [(s.id, s.seq) for s in sequences_b]
    return {"identical": pairs_a == pairs_b}
