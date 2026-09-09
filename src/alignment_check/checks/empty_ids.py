"""Error check: empty sequence IDs."""

from alignment_check.sequence import Sequence


def check_empty_ids(sequences: list[Sequence]) -> dict[str, object]:
    """Flag sequences whose ID is empty.

    Sequences are identified by their position in the input file (rather
    than by ID, since the ID is what's missing).

    Args:
        sequences: The sequences read from the input file.

    Returns:
        A dict with "indices": the 0-based positions of sequences with
        an empty ID.
    """
    indices = [i for i, s in enumerate(sequences) if s.id == ""]
    return {"indices": indices}
