from alignment_check.checks.gc_content import check_gc_content, compute_gc_content
from alignment_check.sequence import Sequence


def test_compute_gc_content_ignores_gaps() -> None:
    values = compute_gc_content([Sequence(id="a", seq="GC--AT")])
    assert values == {"a": 0.5}


def test_compute_gc_content_omits_all_gap_sequence() -> None:
    values = compute_gc_content([Sequence(id="a", seq="----")])
    assert values == {}


def test_check_gc_content_flags_outlier_with_fixed_threshold() -> None:
    sequences = [
        Sequence(id="a", seq="GCGC"),  # 1.0
        Sequence(id="b", seq="ATAT"),  # 0.0
    ]
    result = check_gc_content(sequences, low_threshold=0.2, high_threshold=0.8)
    assert result["outliers"].low_ids == ["b"]
    assert result["outliers"].high_ids == ["a"]


def test_check_gc_content_passes_uniform_sequences() -> None:
    sequences = [Sequence(id="a", seq="GCAT"), Sequence(id="b", seq="GCAT")]
    result = check_gc_content(sequences)
    assert result["outliers"].low_ids == []
    assert result["outliers"].high_ids == []
