from alignment_check.info.per_sequence_summary import compute_per_sequence_summary
from alignment_check.sequence import Sequence


def test_compute_per_sequence_summary() -> None:
    sequences = [
        Sequence(id="a", seq="GC-RN"),
        Sequence(id="all_gap", seq="-----"),
    ]
    result = compute_per_sequence_summary(sequences)
    assert result["rows"] == [
        {
            "id": "a",
            "length": 5,
            "gap_count": 1,
            "gc_content": 0.5,
            "n_count": 1,
            "ambiguous_count": 1,
        },
        {
            "id": "all_gap",
            "length": 5,
            "gap_count": 5,
            "gc_content": None,
            "n_count": 0,
            "ambiguous_count": 0,
        },
    ]


def test_compute_per_sequence_summary_empty_alignment() -> None:
    assert compute_per_sequence_summary([]) == {"rows": []}
