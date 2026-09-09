from alignment_check.alphabet import Alphabet
from alignment_check.checks.mixed_alphabet import check_mixed_alphabet
from alignment_check.sequence import Sequence


def test_check_mixed_alphabet_flags_nucleotide_and_protein_together() -> None:
    sequences = [
        Sequence(id="nt", seq="ACGT"),
        Sequence(id="aa", seq="MKVLETQ"),
    ]
    result = check_mixed_alphabet(sequences)
    assert result["mixed"] is True
    assert result["classifications"] == {
        "nt": Alphabet.NUCLEOTIDE,
        "aa": Alphabet.PROTEIN,
    }


def test_check_mixed_alphabet_passes_all_nucleotide() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGN")]
    result = check_mixed_alphabet(sequences)
    assert result["mixed"] is False


def test_check_mixed_alphabet_ignores_unclassifiable_sequences() -> None:
    sequences = [
        Sequence(id="nt", seq="ACGT"),
        Sequence(id="gaps", seq="----"),
    ]
    result = check_mixed_alphabet(sequences)
    assert result["mixed"] is False
    assert result["classifications"]["gaps"] == Alphabet.UNKNOWN
