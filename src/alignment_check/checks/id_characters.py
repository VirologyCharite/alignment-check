"""Error check: sequence IDs containing characters likely to break
downstream tools (e.g. Newick trees, CSV files).

Whitespace is allowed. This check can be disabled entirely (the
`--allow-all-id-chars` CLI option) by simply not calling it.
"""

from alignment_check.sequence import Sequence

DEFAULT_DISALLOWED_ID_CHARS = ">():,"


def check_id_characters(
    sequences: list[Sequence],
    disallowed_chars: str = DEFAULT_DISALLOWED_ID_CHARS,
) -> dict[str, object]:
    """Flag sequence IDs containing disallowed characters.

    Args:
        sequences: The sequences read from the input file.
        disallowed_chars: Characters that are not allowed in an ID.

    Returns:
        A dict with "flagged": maps the ID of each offending sequence
        to the sorted list of disallowed characters found in it.
    """
    disallowed_set = set(disallowed_chars)
    flagged = {}
    for s in sequences:
        found = sorted(set(s.id) & disallowed_set)
        if found:
            flagged[s.id] = found
    return {"flagged": flagged}
