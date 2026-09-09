"""IUPAC alphabet tables and per-sequence alphabet classification.

Nucleotide and amino acid alphabets overlap (e.g. 'A', 'C', 'G', 'T', and
'N' are all valid single-letter codes in both), so classifying a sequence
requires a tie-break rule. This module always prefers a nucleotide
classification when a sequence's letters fit the (much smaller) nucleotide
alphabet, and only falls back to amino acid otherwise. This matches the
convention used by most alignment tools.
"""

import enum

DEFAULT_GAP_CHARS = "-.?"

# Unambiguous nucleotide bases. Both 'T' and 'U' are accepted.
NUCLEOTIDE_BASES = frozenset("ACGTU")

# IUPAC nucleotide ambiguity codes, keyed by letter, valued by the number of
# bases each represents (its "degeneracy").
NUCLEOTIDE_AMBIGUITY_DEGENERACY = {
    "R": 2, "Y": 2, "S": 2, "W": 2, "K": 2, "M": 2,
    "B": 3, "D": 3, "H": 3, "V": 3,
    "N": 4,
}

NUCLEOTIDE_ALPHABET = NUCLEOTIDE_BASES | frozenset(NUCLEOTIDE_AMBIGUITY_DEGENERACY)

# The 20 standard amino acids.
AMINO_ACID_LETTERS = frozenset("ARNDCQEGHILKMFPSTWYV")

# Amino acid ambiguity codes: B (Asp/Asn), Z (Glu/Gln), J (Leu/Ile), and X
# (any residue).
AMINO_ACID_AMBIGUITY_LETTERS = frozenset("BZJX")

# '*' is a translated stop codon, allowed in protein sequences.
AMINO_ACID_ALPHABET = (
    AMINO_ACID_LETTERS | AMINO_ACID_AMBIGUITY_LETTERS | frozenset("*")
)


class Alphabet(enum.Enum):
    """The alphabet a sequence's non-gap characters were classified as."""

    NUCLEOTIDE = "nucleotide"
    PROTEIN = "protein"
    UNKNOWN = "unknown"


def non_gap_letters(seq: str, gap_chars: str = DEFAULT_GAP_CHARS) -> set[str]:
    """Return the set of upper-cased, non-gap characters in a sequence.

    Args:
        seq: The sequence to inspect.
        gap_chars: Characters treated as alignment gaps and ignored.

    Returns:
        The set of distinct upper-cased characters in `seq` that are not
        gap characters.
    """
    gap_set = set(gap_chars)
    return {c.upper() for c in seq if c not in gap_set}


def classify_alphabet(
    seq: str, gap_chars: str = DEFAULT_GAP_CHARS
) -> Alphabet:
    """Classify a sequence's non-gap letters as nucleotide or protein.

    Nucleotide is preferred whenever the sequence's letters fit the
    nucleotide alphabet (see module docstring). Invalid characters (ones
    that belong to neither alphabet) are ignored here; use
    `invalid_letters` to detect those separately.

    Args:
        seq: The sequence to classify.
        gap_chars: Characters treated as alignment gaps and ignored.

    Returns:
        `Alphabet.NUCLEOTIDE` or `Alphabet.PROTEIN` if the (valid) letters
        fit that alphabet, otherwise `Alphabet.UNKNOWN` (this happens for
        an all-gap sequence, or one containing only invalid characters).
    """
    letters = non_gap_letters(seq, gap_chars)
    valid_letters = letters & (NUCLEOTIDE_ALPHABET | AMINO_ACID_ALPHABET)
    if not valid_letters:
        return Alphabet.UNKNOWN
    if valid_letters <= NUCLEOTIDE_ALPHABET:
        return Alphabet.NUCLEOTIDE
    if valid_letters <= AMINO_ACID_ALPHABET:
        return Alphabet.PROTEIN
    return Alphabet.UNKNOWN


def invalid_letters(seq: str, gap_chars: str = DEFAULT_GAP_CHARS) -> set[str]:
    """Return characters in `seq` that are valid in no recognized alphabet.

    Args:
        seq: The sequence to inspect.
        gap_chars: Characters treated as alignment gaps and ignored.

    Returns:
        The set of upper-cased characters that are neither gap characters,
        nucleotide codes, nor amino acid codes.
    """
    letters = non_gap_letters(seq, gap_chars)
    return letters - NUCLEOTIDE_ALPHABET - AMINO_ACID_ALPHABET
