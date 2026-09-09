from alignment_check.checks.empty_sequences import check_empty_sequences
from alignment_check.sequence import Sequence


def test_check_empty_sequences_flags_all_gap_and_all_n() -> None:
    sequences = [
        Sequence(id="clean", seq="ACGT"),
        Sequence(id="gaps", seq="----"),
        Sequence(id="ns", seq="NNNN"),
        Sequence(id="mixed_gaps_ns", seq="--NN"),
        Sequence(id="lowercase_ns", seq="nnnn"),
    ]
    result = check_empty_sequences(sequences)
    assert result["all_gap_ids"] == ["gaps"]
    assert result["all_n_ids"] == ["ns", "mixed_gaps_ns", "lowercase_ns"]
    assert result["flagged_ids"] == [
        "gaps", "lowercase_ns", "mixed_gaps_ns", "ns",
    ]


def test_check_empty_sequences_passes_clean_sequence() -> None:
    result = check_empty_sequences([Sequence(id="clean", seq="ACGT")])
    assert result["flagged_ids"] == []


def test_check_empty_sequences_custom_gap_chars() -> None:
    result = check_empty_sequences(
        [Sequence(id="a", seq="####")], gap_chars="#"
    )
    assert result["all_gap_ids"] == ["a"]
