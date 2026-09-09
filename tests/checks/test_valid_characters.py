from alignment_check.checks.valid_characters import check_valid_characters
from alignment_check.sequence import Sequence


def test_check_valid_characters_flags_invalid_symbols() -> None:
    sequences = [
        Sequence(id="clean", seq="ACGT"),
        Sequence(id="bad", seq="ACG123"),
    ]
    result = check_valid_characters(sequences)
    assert result["flagged"] == {"bad": ["1", "2", "3"]}


def test_check_valid_characters_passes_valid_sequence() -> None:
    result = check_valid_characters([Sequence(id="a", seq="ACGTN-")])
    assert result["flagged"] == {}


def test_check_valid_characters_custom_gap_chars() -> None:
    # '#' isn't a nucleotide/protein code, but it is a gap char here.
    result = check_valid_characters([Sequence(id="a", seq="AC#GT")], gap_chars="#")
    assert result["flagged"] == {}
