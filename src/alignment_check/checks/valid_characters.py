"""Error check: sequence characters that aren't valid for any recognized
alphabet at all (not nucleotide, not amino acid, not a recognized
gap/ambiguity code).
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS, invalid_letters
from alignment_check.sequence import Sequence


def check_valid_characters(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Flag sequences containing genuinely invalid characters.

    Args:
        sequences: The sequences to check.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "flagged": maps the ID of each offending sequence to
        the sorted list of invalid characters found in it.
    """
    flagged = {}
    for s in sequences:
        bad = invalid_letters(s.seq, gap_chars)
        if bad:
            flagged[s.id] = sorted(bad)
    return {"flagged": flagged}
