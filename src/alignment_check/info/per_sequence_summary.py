"""Info: a per-sequence summary table (length, gap count, G/C%, N count,
ambiguous-code count).

Reuses the same metric-computation functions the anomaly checks use, so
the table's numbers always match what those checks flagged.
"""

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.checks.ambiguous_count import compute_ambiguous_counts
from alignment_check.checks.gap_count import compute_gap_counts
from alignment_check.checks.gc_content import compute_gc_content
from alignment_check.checks.n_count import compute_n_counts
from alignment_check.sequence import Sequence


def compute_per_sequence_summary(
    sequences: list[Sequence], gap_chars: str = DEFAULT_GAP_CHARS
) -> dict[str, object]:
    """Build a per-sequence summary table.

    Args:
        sequences: The sequences to summarize.
        gap_chars: Characters treated as alignment gaps.

    Returns:
        A dict with "rows": a list of per-sequence dicts, each with
        "id", "length", "gap_count", "gc_content" (None if the sequence
        has no non-gap characters), "n_count", and "ambiguous_count".
    """
    gap_counts = compute_gap_counts(sequences, gap_chars)
    gc_content = compute_gc_content(sequences, gap_chars)
    n_counts = compute_n_counts(sequences)
    ambiguous_counts = compute_ambiguous_counts(sequences)

    rows = [
        {
            "id": s.id,
            "length": len(s.seq),
            "gap_count": gap_counts[s.id]["gap_count"],
            "gc_content": gc_content.get(s.id),
            "n_count": n_counts[s.id],
            "ambiguous_count": ambiguous_counts[s.id],
        }
        for s in sequences
    ]
    return {"rows": rows}
