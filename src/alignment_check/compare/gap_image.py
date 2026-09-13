"""Builds the data for a gap-position image: one row per sequence, one
column per alignment site, 1 where that sequence has a gap.

By default, columns where none of the given (row_order) sequences have a
gap are left out entirely, keeping the image compact -- this means the
result can't be compared column-for-column against the same image built
for a different alignment, only used to get a visual sense of the
number and distribution of gaps. Passing `include_ungapped_sites=True`
keeps every column, at the cost of a much wider image for long
alignments.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence


def compute_gap_image_rows(
    sequences: list[Sequence],
    row_order: list[str],
    gap_chars: str = DEFAULT_GAP_CHARS,
    include_ungapped_sites: bool = False,
) -> dict[str, object]:
    """Build a 0/1 gap-position grid for the given sequences.

    Args:
        sequences: The alignment's sequences.
        row_order: The IDs to include, and in what order (top to
            bottom); typically the common IDs, ordered as in the first
            alignment.
        gap_chars: Characters treated as alignment gaps.
        include_ungapped_sites: If False (the default), columns with no
            gap in any of `row_order`'s sequences are omitted. If True,
            every column is included.

    Returns:
        A dict with:
            "grid": A list of rows (one per `row_order` ID), each a list
                of 0/1 values (1 = gap) for the shown columns.
            "row_ids": `row_order`, unchanged (for labeling).
            "columns": The 0-based real alignment column index behind
                each shown column, in order (so callers can label a
                shown column with its true position even when columns
                have been compressed out).
            "num_columns_shown": How many columns are in `grid`.
            "num_columns_total": The alignment's actual width.
    """
    by_id = {s.id: s.seq for s in sequences}
    gap_set = set(gap_chars)
    width = len(by_id[row_order[0]]) if row_order else 0

    if include_ungapped_sites:
        columns = list(range(width))
    else:
        columns = [
            col
            for col in range(width)
            if any(by_id[id_][col] in gap_set for id_ in row_order)
        ]

    grid = [
        [1 if by_id[id_][col] in gap_set else 0 for col in columns]
        for id_ in row_order
    ]

    return {
        "grid": grid,
        "row_ids": row_order,
        "columns": columns,
        "num_columns_shown": len(columns),
        "num_columns_total": width,
    }


def chunk_gap_image_rows(
    image_data: dict[str, object], window_size: int | None
) -> list[dict[str, object]]:
    """Split one image's shown columns into consecutive, same-sized windows.

    Rows (`row_ids`) are identical in every chunk; only which columns of
    `grid`/`columns` each chunk covers differs.

    Args:
        image_data: The return value of `compute_gap_image_rows`.
        window_size: Maximum number of shown columns per chunk. None (or
            a value at least as large as the image) means one chunk
            covering everything -- i.e. no splitting.

    Returns:
        The chunks, in column order. Always at least one, even for a
        zero-column image (matching `compute_gap_image_rows`'s own
        handling of that case).
    """
    columns = image_data["columns"]
    total = len(columns)

    if not window_size or window_size >= total:
        return [image_data]

    grid = image_data["grid"]
    return [
        {
            "grid": [row[start : start + window_size] for row in grid],
            "row_ids": image_data["row_ids"],
            "columns": columns[start : start + window_size],
            "num_columns_shown": min(window_size, total - start),
            "num_columns_total": image_data["num_columns_total"],
        }
        for start in range(0, total, window_size)
    ]
