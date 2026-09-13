from alignment_check.compare.gap_image import (
    chunk_gap_image_rows,
    compute_gap_image_rows,
)
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


def test_chunk_gap_image_rows_splits_into_windows() -> None:
    # 10 columns, no gaps -- use include_ungapped_sites so none are
    # compressed away.
    sequences = [Sequence(id="a", seq="ACGTACGTAC")]
    image_data = compute_gap_image_rows(
        sequences, ["a"], include_ungapped_sites=True
    )
    chunks = chunk_gap_image_rows(image_data, window_size=4)
    assert len(chunks) == 3
    assert [c["columns"] for c in chunks] == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
    assert [c["num_columns_shown"] for c in chunks] == [4, 4, 2]
    assert all(c["num_columns_total"] == 10 for c in chunks)
    assert all(c["row_ids"] == ["a"] for c in chunks)
    assert chunks[1]["grid"] == [list(image_data["grid"][0][4:8])]


def test_chunk_gap_image_rows_no_window_size_returns_single_chunk() -> None:
    sequences = [Sequence(id="a", seq="ACGT")]
    image_data = compute_gap_image_rows(sequences, ["a"], include_ungapped_sites=True)
    chunks = chunk_gap_image_rows(image_data, window_size=None)
    assert chunks == [image_data]


def test_chunk_gap_image_rows_oversized_window_returns_single_chunk() -> None:
    sequences = [Sequence(id="a", seq="ACGT")]
    image_data = compute_gap_image_rows(
        sequences, ["a"], include_ungapped_sites=True
    )
    chunks = chunk_gap_image_rows(image_data, window_size=100)
    assert chunks == [image_data]


def test_chunk_gap_image_rows_empty_image_returns_single_empty_chunk() -> None:
    image_data = compute_gap_image_rows([], [])
    chunks = chunk_gap_image_rows(image_data, window_size=5)
    assert chunks == [image_data]
