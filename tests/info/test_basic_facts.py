from alignment_check.info.basic_facts import compute_basic_facts
from alignment_check.sequence import Sequence


def test_compute_basic_facts_uniform_lengths() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")]
    result = compute_basic_facts(sequences)
    assert result == {"num_sequences": 2, "lengths": [4]}


def test_compute_basic_facts_mismatched_lengths() -> None:
    sequences = [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACG")]
    result = compute_basic_facts(sequences)
    assert result == {"num_sequences": 2, "lengths": [3, 4]}


def test_compute_basic_facts_empty_alignment() -> None:
    assert compute_basic_facts([]) == {"num_sequences": 0, "lengths": []}
