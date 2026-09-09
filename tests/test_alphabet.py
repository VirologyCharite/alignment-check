import pytest

from alignment_check.alphabet import (
    Alphabet,
    classify_alphabet,
    invalid_letters,
    non_gap_letters,
)


@pytest.mark.parametrize(
    "seq,expected",
    [
        ("ACGT", {"A", "C", "G", "T"}),
        ("acgt", {"A", "C", "G", "T"}),
        ("A-C.G?T", {"A", "C", "G", "T"}),
        ("----", set()),
    ],
)
def test_non_gap_letters(seq: str, expected: set[str]) -> None:
    assert non_gap_letters(seq) == expected


def test_non_gap_letters_custom_gap_chars() -> None:
    assert non_gap_letters("A#C_G", gap_chars="#_") == {"A", "C", "G"}


@pytest.mark.parametrize(
    "seq,expected",
    [
        ("ACGT", Alphabet.NUCLEOTIDE),
        ("acgtu", Alphabet.NUCLEOTIDE),
        ("ACGTN", Alphabet.NUCLEOTIDE),
        ("ACGTRYSWKMBDHVN", Alphabet.NUCLEOTIDE),
        ("ACG-T.T?T", Alphabet.NUCLEOTIDE),
        ("MKVLETQ", Alphabet.PROTEIN),
        ("MKVLETQ*", Alphabet.PROTEIN),
        ("MKVLETQBZJX", Alphabet.PROTEIN),
        ("----", Alphabet.UNKNOWN),
        ("123", Alphabet.UNKNOWN),
    ],
)
def test_classify_alphabet(seq: str, expected: Alphabet) -> None:
    assert classify_alphabet(seq) == expected


def test_classify_alphabet_prefers_nucleotide_on_overlap() -> None:
    # 'ACGT' fits both alphabets; nucleotide wins the tie-break.
    assert classify_alphabet("ACGT") == Alphabet.NUCLEOTIDE


@pytest.mark.parametrize(
    "seq,expected",
    [
        ("ACGT", set()),
        ("MKVLETQ", set()),
        ("ACG123", {"1", "2", "3"}),
        ("ACGZ", set()),  # Z is a valid (protein) ambiguity code.
    ],
)
def test_invalid_letters(seq: str, expected: set[str]) -> None:
    assert invalid_letters(seq) == expected
