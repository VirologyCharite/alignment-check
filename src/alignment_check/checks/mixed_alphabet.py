"""Error check: mixed nucleotide and amino acid sequences in one alignment."""

from alignment_check.alphabet import DEFAULT_GAP_CHARS, Alphabet, classify_alphabet
from alignment_check.sequence import Sequence


def check_mixed_alphabet(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Flag an alignment that mixes nucleotide and amino acid sequences.

    Each sequence is classified independently (see
    `alignment_check.alphabet.classify_alphabet`); sequences that cannot
    be classified (e.g. all-gap ones) are ignored. Callers should
    exclude sequences already flagged by `check_empty_sequences` before
    calling this.

    Args:
        sequences: The sequences to classify.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with:
            "mixed": True if both nucleotide and protein sequences are
                present.
            "classifications": Maps each sequence ID to its classified
                `Alphabet`.
    """
    classifications = {
        s.id: classify_alphabet(s.seq, gap_chars) for s in sequences
    }
    found = {a for a in classifications.values() if a != Alphabet.UNKNOWN}
    return {
        "mixed": len(found) > 1,
        "classifications": classifications,
    }
