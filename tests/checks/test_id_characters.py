from alignment_check.checks.id_characters import check_id_characters
from alignment_check.sequence import Sequence


def test_check_id_characters_flags_disallowed_characters() -> None:
    sequences = [
        Sequence(id="seq(1)", seq="ACGT"),
        Sequence(id="a,b:c", seq="ACGA"),
        Sequence(id="clean_id", seq="ACGG"),
    ]
    result = check_id_characters(sequences)
    assert result["flagged"] == {
        "seq(1)": ["(", ")"],
        "a,b:c": [",", ":"],
    }


def test_check_id_characters_allows_whitespace() -> None:
    sequences = [Sequence(id="my seq id", seq="ACGT")]
    result = check_id_characters(sequences)
    assert result["flagged"] == {}


def test_check_id_characters_custom_disallowed_chars() -> None:
    sequences = [Sequence(id="a#b", seq="ACGT")]
    result = check_id_characters(sequences, disallowed_chars="#")
    assert result["flagged"] == {"a#b": ["#"]}
