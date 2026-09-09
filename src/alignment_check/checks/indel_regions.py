"""Anomaly check: contiguous insertion/deletion regions present in only a
minority of sequences.

At each column, sequences are split into a gapped group and an ungapped
group; whichever group is smaller is the "minority" for that column
(its `kind` is "deletion" if the minority has the gap, "insertion" if
the minority has the base). Consecutive columns that share the exact
same minority group and kind are merged into one region; only regions
at least `min_length` columns long are reported.

Requires all sequences to be the same length; callers should skip this
when `equal_lengths.check_equal_lengths` reports "consistent": False.
"""

import itertools
from dataclasses import dataclass

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.sequence import Sequence

DEFAULT_MINORITY_FRACTION = 0.10
DEFAULT_MIN_LENGTH = 10

# The per-column classification used to group consecutive columns: the
# minority sequence IDs at that column, and whether the minority is the
# gapped or ungapped group. None means the column has no minority (its
# gapped/ungapped split isn't lopsided enough to qualify).
_ColumnKey = tuple[frozenset[str], str] | None


def _column_key(
    sequences: list[Sequence], col: int, gap_set: set[str], minority_fraction: float
) -> _ColumnKey:
    n = len(sequences)
    gapped_ids = frozenset(s.id for s in sequences if s.seq[col] in gap_set)
    ungapped_ids = frozenset(s.id for s in sequences) - gapped_ids
    if len(gapped_ids) <= len(ungapped_ids):
        minority_ids, kind = gapped_ids, "deletion"
    else:
        minority_ids, kind = ungapped_ids, "insertion"

    fraction = len(minority_ids) / n
    if 0 < fraction < minority_fraction:
        return (minority_ids, kind)
    return None


@dataclass(frozen=True)
class IndelRegion:
    """One contiguous minority insertion/deletion region.

    Attributes:
        start: 0-based index of the region's first column.
        end: 0-based index of the region's last column (inclusive).
        length: Number of columns in the region.
        minority_ids: IDs of the sequences in the minority, sorted.
        kind: "insertion" if the minority sequences have bases where the
            majority has gaps, "deletion" if the reverse.
    """

    start: int
    end: int
    length: int
    minority_ids: list[str]
    kind: str


def find_indel_regions(
    sequences: list[Sequence],
    gap_chars: str = DEFAULT_GAP_CHARS,
    minority_fraction: float = DEFAULT_MINORITY_FRACTION,
    min_length: int = DEFAULT_MIN_LENGTH,
) -> list[IndelRegion]:
    """Find contiguous minority insertion/deletion regions.

    Args:
        sequences: The (equal-length) sequences to check.
        gap_chars: Characters treated as alignment gaps.
        minority_fraction: A column's minority group must be smaller
            than this fraction of all sequences to count as a minority.
        min_length: The minimum number of consecutive matching columns
            to report as a region.

    Returns:
        The qualifying regions, in column order.
    """
    if not sequences:
        return []

    gap_set = set(gap_chars)
    length = len(sequences[0].seq)
    keys = [
        _column_key(sequences, col, gap_set, minority_fraction)
        for col in range(length)
    ]

    regions = []
    col = 0
    for key, group in itertools.groupby(keys):
        group_length = sum(1 for _ in group)
        if key is not None and group_length >= min_length:
            minority_ids, kind = key
            regions.append(
                IndelRegion(
                    start=col,
                    end=col + group_length - 1,
                    length=group_length,
                    minority_ids=sorted(minority_ids),
                    kind=kind,
                )
            )
        col += group_length
    return regions


def check_indel_regions(
    sequences: list[Sequence],
    gap_chars: str = DEFAULT_GAP_CHARS,
    minority_fraction: float = DEFAULT_MINORITY_FRACTION,
    min_length: int = DEFAULT_MIN_LENGTH,
) -> dict[str, object]:
    """Flag contiguous minority insertion/deletion regions.

    Args:
        sequences: The (equal-length) sequences to check.
        gap_chars: Characters treated as alignment gaps.
        minority_fraction: See `find_indel_regions`.
        min_length: See `find_indel_regions`.

    Returns:
        A dict with "regions" (a list of `IndelRegion`).
    """
    regions = find_indel_regions(sequences, gap_chars, minority_fraction, min_length)
    return {"regions": regions}
