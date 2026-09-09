"""Anomaly check: long stretches of ambiguous/'N' characters within an
otherwise clean sequence.

This is distinct from the whole-sequence ambiguous/N counts (see
`ambiguous_count` and `n_count`): it localizes the problem to one run
within a sequence, rather than counting occurrences across the whole
sequence. Callers should exclude sequences already flagged by those
whole-sequence checks (pass their IDs as `exclude_ids`), since a
sequence that's ambiguous throughout isn't "otherwise clean".
"""

from dataclasses import dataclass

from alignment_check.alphabet import NUCLEOTIDE_AMBIGUITY_DEGENERACY
from alignment_check.sequence import Sequence

DEFAULT_MIN_LENGTH_FRACTION = 0.10

AMBIGUOUS_OR_N = frozenset(NUCLEOTIDE_AMBIGUITY_DEGENERACY)


@dataclass(frozen=True)
class AmbiguousRun:
    """The longest run of ambiguous/'N' characters found in a sequence.

    Attributes:
        start: 0-based index of the run's first character.
        length: Number of characters in the run.
    """

    start: int
    length: int


def longest_ambiguous_run(seq: str) -> AmbiguousRun:
    """Find the longest run of ambiguous/'N' characters in a sequence.

    Args:
        seq: The sequence to scan.

    Returns:
        The longest run found (start=0, length=0 if there is none).
    """
    best_start = 0
    best_length = 0
    current_start = 0
    current_length = 0
    for i, c in enumerate(seq):
        if c.upper() in AMBIGUOUS_OR_N:
            if current_length == 0:
                current_start = i
            current_length += 1
            if current_length > best_length:
                best_start = current_start
                best_length = current_length
        else:
            current_length = 0
    return AmbiguousRun(start=best_start, length=best_length)


def check_long_ambiguous_stretches(
    sequences: list[Sequence],
    exclude_ids: frozenset[str] = frozenset(),
    min_length_fraction: float = DEFAULT_MIN_LENGTH_FRACTION,
) -> dict[str, object]:
    """Flag sequences with a long localized run of ambiguous/'N' characters.

    Args:
        sequences: The sequences to check.
        exclude_ids: Sequence IDs to skip (e.g. ones already flagged by
            the whole-sequence ambiguous/N-count checks).
        min_length_fraction: A run must be at least this fraction of the
            sequence's length to be flagged.

    Returns:
        A dict with "flagged": maps the ID of each offending sequence to
        its `AmbiguousRun`.
    """
    flagged = {}
    for s in sequences:
        if s.id in exclude_ids or not s.seq:
            continue
        run = longest_ambiguous_run(s.seq)
        if run.length >= min_length_fraction * len(s.seq) and run.length > 0:
            flagged[s.id] = run
    return {"flagged": flagged}
