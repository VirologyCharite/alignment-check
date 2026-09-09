"""Info: basic facts about the alignment (sequence count and length)."""

from alignment_check.sequence import Sequence


def compute_basic_facts(sequences: list[Sequence]) -> dict[str, object]:
    """Report the number of sequences and their length(s).

    Args:
        sequences: The sequences to summarize.

    Returns:
        A dict with:
            "num_sequences": How many sequences there are.
            "lengths": The distinct sequence lengths present, sorted.
                Usually a single value; more than one means the
                sequences aren't all the same length.
    """
    return {
        "num_sequences": len(sequences),
        "lengths": sorted({len(s.seq) for s in sequences}),
    }
