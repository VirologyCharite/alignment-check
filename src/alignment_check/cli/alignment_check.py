"""CLI entry point: assess a multiple sequence alignment and write an HTML
report.

This script owns all the orchestration: it calls each check/info library
function directly (there is no registry or auto-discovery), decides
which checks apply given the alignment's alphabet and whether sequence
lengths are consistent, and hands the gathered results to
`alignment_check.report.render_html_report`.
"""

import argparse
import html
import sys
from pathlib import Path

from alignment_check.alphabet import DEFAULT_GAP_CHARS, Alphabet, classify_alphabet
from alignment_check.checks.ambiguous_count import check_ambiguous_count
from alignment_check.checks.duplicate_ids import check_duplicate_ids
from alignment_check.checks.empty_alignment import check_empty_alignment
from alignment_check.checks.empty_ids import check_empty_ids
from alignment_check.checks.empty_sequences import check_empty_sequences
from alignment_check.checks.equal_lengths import check_equal_lengths
from alignment_check.checks.gap_count import check_gap_count
from alignment_check.checks.gap_only_columns import check_gap_only_columns
from alignment_check.checks.gc_content import check_gc_content
from alignment_check.checks.id_characters import (
    DEFAULT_DISALLOWED_ID_CHARS,
    check_id_characters,
)
from alignment_check.checks.indel_regions import (
    DEFAULT_MIN_LENGTH as DEFAULT_INDEL_MIN_LENGTH,
)
from alignment_check.checks.indel_regions import (
    DEFAULT_MINORITY_FRACTION,
    check_indel_regions,
)
from alignment_check.checks.long_ambiguous_stretches import (
    DEFAULT_MIN_LENGTH_FRACTION,
    check_long_ambiguous_stretches,
)
from alignment_check.checks.mixed_alphabet import check_mixed_alphabet
from alignment_check.checks.n_count import check_n_count
from alignment_check.checks.single_sequence import check_single_sequence
from alignment_check.checks.valid_characters import check_valid_characters
from alignment_check.exceptions import AlignmentFileNotFoundError, NotFastaError
from alignment_check.info.basic_facts import compute_basic_facts
from alignment_check.info.majority_frequency import compute_majority_frequencies
from alignment_check.info.majority_frequency_plot import render_majority_frequency_plot
from alignment_check.info.pairwise_identity_histogram import (
    compute_pairwise_identity_histogram,
)
from alignment_check.info.pairwise_identity_histogram_plot import (
    render_pairwise_identity_histogram_plot,
)
from alignment_check.info.per_sequence_summary import compute_per_sequence_summary
from alignment_check.info.site_ambiguity import compute_site_ambiguity
from alignment_check.info.site_ambiguity_plot import render_site_ambiguity_plot
from alignment_check.info.site_gaps import compute_site_gap_fractions
from alignment_check.info.site_gaps_plot import render_site_gaps_plot
from alignment_check.info.site_homogeneity import compute_site_homogeneity
from alignment_check.info.site_homogeneity_plot import render_site_homogeneity_plot
from alignment_check.loader import load_sequences
from alignment_check.report import render_html_report
from alignment_check.sequence import Sequence


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse command-line arguments for the `alignment-check` script."""
    parser = argparse.ArgumentParser(
        description=(
            "Assess a multiple sequence alignment (FASTA) and write an "
            "HTML report of its errors, anomalies, and general "
            "information."
        )
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Input FASTA alignment file (default: read from standard input).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="alignment_check_report.html",
        help="Path to write the HTML report to (default: %(default)s).",
    )
    parser.add_argument(
        "--gap-chars",
        default=DEFAULT_GAP_CHARS,
        help="Characters treated as alignment gaps (default: %(default)r).",
    )
    parser.add_argument(
        "--allow-all-id-chars",
        action="store_true",
        help="Disable the check for sequence ID characters that can break "
        "downstream tools.",
    )
    parser.add_argument(
        "--n2",
        action="store_true",
        help="Enable O(n^2) analyses (currently: the pairwise identity "
        "histogram).",
    )
    parser.add_argument(
        "--gc-low", type=float, help="Fixed low threshold for G/C content."
    )
    parser.add_argument(
        "--gc-high", type=float, help="Fixed high threshold for G/C content."
    )
    parser.add_argument(
        "--gap-count-low", type=float, help="Fixed low threshold for gap count."
    )
    parser.add_argument(
        "--gap-count-high", type=float, help="Fixed high threshold for gap count."
    )
    parser.add_argument(
        "--n-count-low", type=float, help="Fixed low threshold for N count."
    )
    parser.add_argument(
        "--n-count-high", type=float, help="Fixed high threshold for N count."
    )
    parser.add_argument(
        "--ambiguous-count-low",
        type=float,
        help="Fixed low threshold for ambiguous nucleotide code count.",
    )
    parser.add_argument(
        "--ambiguous-count-high",
        type=float,
        help="Fixed high threshold for ambiguous nucleotide code count.",
    )
    parser.add_argument(
        "--indel-minority-fraction",
        type=float,
        default=DEFAULT_MINORITY_FRACTION,
        help="A column's minority group must be smaller than this fraction "
        "of all sequences to be treated as a candidate indel column "
        "(default: %(default)s).",
    )
    parser.add_argument(
        "--indel-min-length",
        type=int,
        default=DEFAULT_INDEL_MIN_LENGTH,
        help="Minimum number of consecutive columns to report as an indel "
        "region (default: %(default)s).",
    )
    parser.add_argument(
        "--long-stretch-fraction",
        type=float,
        default=DEFAULT_MIN_LENGTH_FRACTION,
        help="Minimum length, as a fraction of sequence length, of a run of "
        "ambiguous/N characters to be flagged (default: %(default)s).",
    )
    return parser.parse_args(argv)


def _flagged_ids_detail(ids: list[str]) -> str:
    return ", ".join(html.escape(id_) for id_ in ids) if ids else ""


def _build_load_error_results(input_name: str, message: str) -> dict[str, object]:
    return {
        "input_name": input_name,
        "load_error": {"message": message},
    }


def _build_errors(
    sequences: list[Sequence],
    analysis_sequences: list[Sequence],
    gap_chars: str,
    check_id_chars: bool,
) -> tuple[list[dict[str, object]], list[str]]:
    """Run every error check and return (items, all_gap_or_n_ids)."""
    items = []

    empty = check_empty_alignment(sequences)
    items.append(
        {
            "name": "empty_alignment",
            "failed": empty["empty"],
            "summary": "Alignment is not empty",
            "detail_html": "",
        }
    )

    single = check_single_sequence(sequences)
    items.append(
        {
            "name": "single_sequence",
            "failed": single["single"],
            "summary": "Alignment has more than one sequence",
            "detail_html": "",
        }
    )

    lengths = check_equal_lengths(sequences)
    items.append(
        {
            "name": "equal_lengths",
            "failed": not lengths["consistent"],
            "summary": "All sequences are the same length",
            "detail_html": (
                f"Lengths found: {lengths['unique_lengths']}"
                if not lengths["consistent"]
                else ""
            ),
        }
    )

    empty_seqs = check_empty_sequences(sequences, gap_chars)
    flagged_ids = empty_seqs["flagged_ids"]
    items.append(
        {
            "name": "empty_sequences",
            "failed": bool(flagged_ids),
            "summary": "No all-gap or all-N sequences",
            "detail_html": _flagged_ids_detail(flagged_ids),
        }
    )

    mixed = check_mixed_alphabet(analysis_sequences, gap_chars)
    items.append(
        {
            "name": "mixed_alphabet",
            "failed": mixed["mixed"],
            "summary": "Sequences are not a mix of nucleotide and protein",
            "detail_html": "",
        }
    )

    duplicates = check_duplicate_ids(sequences)
    items.append(
        {
            "name": "duplicate_ids",
            "failed": bool(duplicates["duplicate_ids"]),
            "summary": "No duplicate sequence IDs",
            "detail_html": _flagged_ids_detail(duplicates["duplicate_ids"]),
        }
    )

    empty_ids = check_empty_ids(sequences)
    items.append(
        {
            "name": "empty_ids",
            "failed": bool(empty_ids["indices"]),
            "summary": "No empty sequence IDs",
            "detail_html": (
                f"At positions: {empty_ids['indices']}"
                if empty_ids["indices"]
                else ""
            ),
        }
    )

    if check_id_chars:
        id_chars = check_id_characters(sequences, DEFAULT_DISALLOWED_ID_CHARS)
        items.append(
            {
                "name": "id_characters",
                "failed": bool(id_chars["flagged"]),
                "summary": "No sequence IDs with problematic characters",
                "detail_html": _flagged_ids_detail(list(id_chars["flagged"])),
            }
        )

    valid_chars = check_valid_characters(sequences, gap_chars)
    items.append(
        {
            "name": "valid_characters",
            "failed": bool(valid_chars["flagged"]),
            "summary": "No invalid sequence characters",
            "detail_html": _flagged_ids_detail(list(valid_chars["flagged"])),
        }
    )

    return items, flagged_ids


def _overall_alphabet(sequences: list[Sequence], gap_chars: str) -> Alphabet:
    counts: dict[Alphabet, int] = {}
    for s in sequences:
        alphabet = classify_alphabet(s.seq, gap_chars)
        if alphabet != Alphabet.UNKNOWN:
            counts[alphabet] = counts.get(alphabet, 0) + 1
    if not counts:
        return Alphabet.UNKNOWN
    return max(counts, key=lambda a: counts[a])


def _build_anomalies(
    sequences: list[Sequence], args: argparse.Namespace, is_nucleotide: bool
) -> list[dict[str, object]]:
    items = []

    gc = check_gc_content(sequences, args.gap_chars, args.gc_low, args.gc_high)
    if is_nucleotide:
        gc_flagged = gc["outliers"].low_ids + gc["outliers"].high_ids
        items.append(
            {
                "name": "gc_content",
                "failed": bool(gc_flagged),
                "summary": "No sequences with unusual G/C content",
                "detail_html": _flagged_ids_detail(gc_flagged),
            }
        )

    gap_count = check_gap_count(
        sequences, args.gap_chars, args.gap_count_low, args.gap_count_high
    )
    gap_count_flagged = gap_count["outliers"].low_ids + gap_count["outliers"].high_ids
    items.append(
        {
            "name": "gap_count",
            "failed": bool(gap_count_flagged),
            "summary": "No sequences with an unusual gap count",
            "detail_html": _flagged_ids_detail(gap_count_flagged),
        }
    )

    n_count = check_n_count(sequences, args.n_count_low, args.n_count_high)
    n_count_flagged = n_count["outliers"].low_ids + n_count["outliers"].high_ids
    items.append(
        {
            "name": "n_count",
            "failed": bool(n_count_flagged),
            "summary": "No sequences with an unusual N count",
            "detail_html": _flagged_ids_detail(n_count_flagged),
        }
    )

    ambiguous_flagged: list[str] = []
    if is_nucleotide:
        ambiguous = check_ambiguous_count(
            sequences, args.ambiguous_count_low, args.ambiguous_count_high
        )
        ambiguous_flagged = (
            ambiguous["outliers"].low_ids + ambiguous["outliers"].high_ids
        )
        items.append(
            {
                "name": "ambiguous_count",
                "failed": bool(ambiguous_flagged),
                "summary": "No sequences with an unusual ambiguous-code count",
                "detail_html": _flagged_ids_detail(ambiguous_flagged),
            }
        )

    lengths_consistent = check_equal_lengths(sequences)["consistent"]
    if lengths_consistent:
        gap_only = check_gap_only_columns(sequences, args.gap_chars)
        items.append(
            {
                "name": "gap_only_columns",
                "failed": bool(gap_only["columns"]),
                "summary": "No gap-only columns",
                "detail_html": (
                    f"{gap_only['count']} column(s): {gap_only['columns']}"
                    if gap_only["columns"]
                    else ""
                ),
            }
        )

        indel = check_indel_regions(
            sequences,
            args.gap_chars,
            args.indel_minority_fraction,
            args.indel_min_length,
        )
        items.append(
            {
                "name": "indel_regions",
                "failed": bool(indel["regions"]),
                "summary": "No minority indel regions",
                "detail_html": "; ".join(
                    f"{r.kind} at columns {r.start}-{r.end} "
                    f"({html.escape(', '.join(r.minority_ids))})"
                    for r in indel["regions"]
                ),
            }
        )

    if is_nucleotide:
        exclude_ids = frozenset(n_count_flagged) | frozenset(ambiguous_flagged)
        long_stretches = check_long_ambiguous_stretches(
            sequences, exclude_ids, args.long_stretch_fraction
        )
        items.append(
            {
                "name": "long_ambiguous_stretches",
                "failed": bool(long_stretches["flagged"]),
                "summary": "No long localized ambiguous/N stretches",
                "detail_html": _flagged_ids_detail(list(long_stretches["flagged"])),
            }
        )

    return items


def _build_plots(
    sequences: list[Sequence], args: argparse.Namespace, is_nucleotide: bool
) -> list[dict[str, object]]:
    plots = []
    first = True

    def include_plotlyjs() -> bool:
        nonlocal first
        result = first
        first = False
        return result

    if not check_equal_lengths(sequences)["consistent"]:
        return plots

    site_gaps = compute_site_gap_fractions(sequences, args.gap_chars)
    plots.append(
        {
            "title": "Site gap fraction",
            "html": render_site_gaps_plot(site_gaps, include_plotlyjs()),
        }
    )

    majority = compute_majority_frequencies(sequences, args.gap_chars)
    plots.append(
        {
            "title": "Site majority-character frequency",
            "html": render_majority_frequency_plot(majority, include_plotlyjs()),
        }
    )

    if is_nucleotide:
        ambiguity = compute_site_ambiguity(sequences, args.gap_chars)
        plots.append(
            {
                "title": "Site nucleotide ambiguity",
                "html": render_site_ambiguity_plot(ambiguity, include_plotlyjs()),
            }
        )

    homogeneity = compute_site_homogeneity(sequences, args.gap_chars)
    plots.append(
        {
            "title": "Site homogeneity",
            "html": render_site_homogeneity_plot(homogeneity, include_plotlyjs()),
        }
    )

    if args.n2 and len(sequences) >= 2:
        histogram = compute_pairwise_identity_histogram(sequences, args.gap_chars)
        plots.append(
            {
                "title": "Pairwise sequence identity",
                "html": render_pairwise_identity_histogram_plot(
                    histogram, include_plotlyjs()
                ),
            }
        )

    return plots


def build_results(
    input_name: str, sequences: list[Sequence], args: argparse.Namespace
) -> dict[str, object]:
    """Run all checks and info functions and gather them into one dict.

    Args:
        input_name: Name of the input, for display in the report.
        sequences: The sequences read from the input file.
        args: Parsed CLI arguments (see `parse_args`).

    Returns:
        The results dict expected by `report.render_html_report`.
    """
    excluded_ids = check_empty_sequences(sequences, args.gap_chars)["flagged_ids"]
    analysis_sequences = [s for s in sequences if s.id not in set(excluded_ids)]

    error_items, _ = _build_errors(
        sequences, analysis_sequences, args.gap_chars, not args.allow_all_id_chars
    )

    notes = []
    if excluded_ids:
        notes.append(
            f"{len(excluded_ids)} sequence(s) excluded from anomaly/info "
            f"analysis as all-gap or all-N: {', '.join(excluded_ids)}."
        )

    results: dict[str, object] = {
        "input_name": input_name,
        "load_error": None,
        "basic_facts": compute_basic_facts(sequences),
        "errors": error_items,
        "anomalies": [],
        "per_sequence_summary": None,
        "plots": [],
        "notes": notes,
    }

    if not analysis_sequences:
        notes.append("No further analysis performed: no usable sequences remain.")
        return results

    is_nucleotide = (
        _overall_alphabet(analysis_sequences, args.gap_chars) == Alphabet.NUCLEOTIDE
    )
    results["anomalies"] = _build_anomalies(analysis_sequences, args, is_nucleotide)

    summary = compute_per_sequence_summary(analysis_sequences, args.gap_chars)
    summary_headers = [
        "id", "length", "gap_count", "gc_content", "n_count", "ambiguous_count",
    ]
    results["per_sequence_summary"] = {
        "headers": summary_headers,
        "rows": [
            [row[header] for header in summary_headers] for row in summary["rows"]
        ],
    }

    results["plots"] = _build_plots(analysis_sequences, args, is_nucleotide)

    return results


def main(argv: list[str] | None = None) -> None:
    """Entry point for the `alignment-check` console script."""
    args = parse_args(argv)
    input_name = args.file if args.file else "<stdin>"

    try:
        sequences = load_sequences(args.file)
    except (AlignmentFileNotFoundError, NotFastaError) as error:
        results = _build_load_error_results(input_name, str(error))
    else:
        results = build_results(input_name, sequences, args)

    html_report = render_html_report(results)
    Path(args.output).write_text(html_report)
    print(f"Wrote report to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
