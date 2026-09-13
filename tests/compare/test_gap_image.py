from alignment_check.compare.gap_image import compute_gap_image_rows
from alignment_check.sequence import Sequence


def test_compute_gap_image_rows_compresses_ungapped_columns_by_default() -> None:
    sequences = [
        Sequence(id="a", seq="A-CG"),
        Sequence(id="b", seq="ACGT"),
    ]
    result = compute_gap_image_rows(sequences, ["a", "b"])
    # Only column 1 (0-based) has a gap in either row.
    assert result["grid"] == [[1], [0]]
    assert result["row_ids"] == ["a", "b"]
    assert result["columns"] == [1]
    assert result["num_columns_shown"] == 1
    assert result["num_columns_total"] == 4


def test_compute_gap_image_rows_include_ungapped_sites() -> None:
    sequences = [Sequence(id="a", seq="A-CG"), Sequence(id="b", seq="ACGT")]
    result = compute_gap_image_rows(
        sequences, ["a", "b"], include_ungapped_sites=True
    )
    assert result["grid"] == [[0, 1, 0, 0], [0, 0, 0, 0]]
    assert result["columns"] == [0, 1, 2, 3]
    assert result["num_columns_shown"] == 4


def test_compute_gap_image_rows_respects_row_order() -> None:
    sequences = [Sequence(id="a", seq="AC"), Sequence(id="b", seq="-C")]
    result = compute_gap_image_rows(sequences, ["b", "a"])
    assert result["row_ids"] == ["b", "a"]
    assert result["grid"] == [[1], [0]]


def test_compute_gap_image_rows_empty_row_order() -> None:
    result = compute_gap_image_rows([], [])
    assert result == {
        "grid": [],
        "row_ids": [],
        "columns": [],
        "num_columns_shown": 0,
        "num_columns_total": 0,
    }
