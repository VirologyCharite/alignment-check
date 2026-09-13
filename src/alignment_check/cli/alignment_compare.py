"""CLI entry point: compare two multiple sequence alignments and write an
HTML report.

Like `cli/alignment_check.py`, this script owns all the orchestration: it
calls each comparison function directly and hands the gathered results
to `compare.compare_report.render_compare_report`.
"""

import argparse
import html
import sys
from pathlib import Path

from alignment_check.alphabet import DEFAULT_GAP_CHARS
from alignment_check.checks.empty_alignment import check_empty_alignment
from alignment_check.checks.equal_lengths import check_equal_lengths
from alignment_check.checks.gap_only_columns import check_gap_only_columns
from alignment_check.compare.alignment_widths import compare_alignment_widths
from alignment_check.compare.compare_report import render_compare_report
from alignment_check.compare.files_identical import compare_files_identical
from alignment_check.compare.gap_count_scatter_plot import (
    render_gap_count_scatter_plot,
)
from alignment_check.compare.gap_image import compute_gap_image_rows
from alignment_check.compare.gap_image_plot import render_gap_image_plot
from alignment_check.compare.id_order import compare_common_id_order
from alignment_check.compare.id_sets import compare_id_sets
from alignment_check.compare.internal_gap_count import compare_internal_gap_counts
from alignment_check.compare.path_labels import shortest_distinguishing_labels
from alignment_check.compare.preceding_gap_diff import compare_preceding_gap_diffs
from alignment_check.compare.preceding_gap_diff_plot import (
    render_preceding_gap_diff_plot,
)
from alignment_check.compare.sequence_identity import (
    compare_common_sequence_identity,
)
from alignment_check.exceptions import (
    AlignmentFileNotFoundError,
    InvalidAlignmentError,
    NotFastaError,
)
from alignment_check.loader import load_sequences
from alignment_check.sequence import Sequence


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse command-line arguments for the `alignment-compare` script."""
    parser = argparse.ArgumentParser(
        description="Compare two multiple sequence alignments (FASTA) and "
        "write an HTML report of their differences."
    )
    parser.add_argument("file_a", help="First FASTA alignment file.")
    parser.add_argument("file_b", help="Second FASTA alignment file.")
    parser.add_argument(
        "-o",
        "--output",
        default="alignment_compare_report.html",
        help="Path to write the HTML report to (default: %(default)s).",
    )
    parser.add_argument(
        "--gap-chars",
        default=DEFAULT_GAP_CHARS,
        help="Characters treated as alignment gaps (default: %(default)r).",
    )
    parser.add_argument(
        "--exclude-ungapped-sites",
        action="store_true",
        help="Compress the gap-position images down to just the columns "
        "with a gap in some shown sequence, instead of showing every "
        "column (the default). Produces much smaller images, but the "
        "ruler offset on each image is then omitted, since the shown "
        "columns' real positions no longer increase evenly.",
    )
    parser.add_argument(
        "--include-igcps-plot",
        action="store_true",
        help="Include the internal gap count per sequence scatter plot. "
        "Off by default.",
    )
    parser.add_argument(
        "--include-pigd-plot",
        action="store_true",
        help="Include the per-residue internal gap-count difference plot "
        "(one line per common sequence). Off by default: it embeds one "
        "point per residue, which can make the report very large for "
        "long sequences.",
    )
    parser.add_argument(
        "--gap-image-window-size",
        type=int,
        metavar="N",
        help="Split each gap-position image into consecutive chunks of "
        "at most N shown columns, each chunk shown as its own A-over-B "
        "pair, with all the pairs stacked in one vertically-scrollable "
        "area. Default: one pair covering the whole image.",
    )
    args = parser.parse_args(argv)
    if args.gap_image_window_size is not None and args.gap_image_window_size <= 0:
        parser.error("--gap-image-window-size must be a positive integer")
    return args


def _try_load(path: str) -> tuple[list[Sequence] | None, str | None]:
    try:
        return load_sequences(path), None
    except (AlignmentFileNotFoundError, NotFastaError) as error:
        return None, str(error)


def _validate_alignment(sequences: list[Sequence], label: str) -> None:
    """Raise InvalidAlignmentError if `sequences` isn't a usable alignment.

    Every later computation assumes an alignment's own sequences are all
    the same length; this is the one gate all of them rely on.

    Args:
        sequences: The sequences read from one input file.
        label: "A" or "B", for the error message.

    Raises:
        InvalidAlignmentError: If `sequences` is empty, or its sequences
            aren't all the same length.
    """
    if check_empty_alignment(sequences)["empty"]:
        raise InvalidAlignmentError(f"{label} contains no sequences.")
    lengths = check_equal_lengths(sequences)
    if not lengths["consistent"]:
        raise InvalidAlignmentError(
            f"{label}'s sequences are not all the same length "
            f"(lengths found: {lengths['unique_lengths']})."
        )


def _ids_detail(ids: list[str]) -> str:
    return ", ".join(html.escape(id_) for id_ in ids) if ids else ""


def _format_width_comparison(widths_a: list[int], widths_b: list[int]) -> str:
    # By the time this runs, main() has already required each file's own
    # sequences to be a single consistent length (see _validate_alignment).
    width_a, width_b = widths_a[0], widths_b[0]
    return (
        f"Alignment width: A={width_a}, B={width_b} "
        f"(difference: {width_a - width_b:+d})"
    )


def _gap_only_columns_item(
    sequences: list[Sequence], label: str, gap_chars: str
) -> dict[str, object]:
    """Build a tier1 item flagging gap-only columns in one file."""
    columns = check_gap_only_columns(sequences, gap_chars)["columns"]
    return {
        "failed": bool(columns),
        "summary": f"No gap-only columns in {label}",
        "detail_html": f"{len(columns)} column(s): {columns}" if columns else "",
    }


def build_results(
    name_a: str,
    name_b: str,
    full_path_a: str,
    full_path_b: str,
    sequences_a: list[Sequence],
    sequences_b: list[Sequence],
    args: argparse.Namespace,
) -> dict[str, object]:
    """Run every comparison and gather the results into one dict.

    Args:
        name_a: Short, display-friendly name for the first input (used
            as "A" throughout the report, e.g. in plot titles).
        name_b: Short, display-friendly name for the second input.
        full_path_a: The first input's full path, shown once so "A" is
            unambiguous.
        full_path_b: The second input's full path.
        sequences_a: Sequences read from the first input.
        sequences_b: Sequences read from the second input.
        args: Parsed CLI arguments (see `parse_args`).

    Returns:
        The results dict expected by `compare_report.render_compare_report`.
    """
    id_sets = compare_id_sets(sequences_a, sequences_b)
    order = compare_common_id_order(sequences_a, sequences_b, id_sets["common_ids"])
    identity = compare_common_sequence_identity(
        sequences_a, sequences_b, id_sets["common_ids"], args.gap_chars
    )
    widths = compare_alignment_widths(sequences_a, sequences_b)
    identical = compare_files_identical(sequences_a, sequences_b)

    info_lines = [
        f"A: {full_path_a} ({name_a})",
        f"B: {full_path_b} ({name_b})",
        f"Number of sequences: A={len(sequences_a)}, B={len(sequences_b)}",
        _format_width_comparison(widths["widths_a"], widths["widths_b"]),
        "The two files are identical."
        if identical["identical"]
        else "The two files are not identical.",
    ]

    id_sets_detail = "; ".join(
        part
        for part in [
            f"Only in A: {_ids_detail(id_sets['only_in_a'])}"
            if id_sets["only_in_a"]
            else "",
            f"Only in B: {_ids_detail(id_sets['only_in_b'])}"
            if id_sets["only_in_b"]
            else "",
        ]
        if part
    )

    tier1_items = [
        {
            "failed": bool(id_sets["only_in_a"] or id_sets["only_in_b"]),
            "summary": f"Same sequence IDs ({id_sets['num_common']} in common)",
            "detail_html": id_sets_detail,
        },
        {
            "failed": not order["order_matches"],
            "summary": "Common sequence IDs are in the same relative order",
            "detail_html": "",
        },
        {
            "failed": bool(identity["mismatched_ids"]),
            "summary": "Common sequences have identical (ungapped) content",
            "detail_html": _ids_detail(identity["mismatched_ids"]),
        },
    ]
    for sequences, label in ((sequences_a, "A"), (sequences_b, "B")):
        tier1_items.append(
            _gap_only_columns_item(sequences, label, args.gap_chars)
        )

    results: dict[str, object] = {
        "name_a": name_a,
        "name_b": name_b,
        "load_error": None,
        "info_lines": info_lines,
        "tier1_items": tier1_items,
        "tier2_note": None,
        "gap_count_table": None,
        "plots": [],
    }

    mismatched = set(identity["mismatched_ids"])
    usable_ids = [id_ for id_ in id_sets["common_ids"] if id_ not in mismatched]

    if not usable_ids:
        results["tier2_note"] = (
            "No further comparison performed: there are no common "
            "sequences with matching (ungapped) content."
        )
        return results

    gap_counts = compare_internal_gap_counts(
        sequences_a, sequences_b, usable_ids, args.gap_chars
    )
    results["gap_count_table"] = {
        "headers": ["id", "gap_count_a", "gap_count_b", "diff (a - b)"],
        "rows": [
            [
                id_,
                gap_counts["counts_a"][id_],
                gap_counts["counts_b"][id_],
                gap_counts["counts_a"][id_] - gap_counts["counts_b"][id_],
            ]
            for id_ in usable_ids
        ],
    }

    # Each image shows the usable common sequences, then (below a red
    # divider drawn by render_gap_image_plot) any sequences unique to
    # that one file, in the order they appear in it.
    row_order_a = usable_ids + id_sets["only_in_a"]
    row_order_b = usable_ids + id_sets["only_in_b"]
    divider_after_row_a = len(usable_ids) if id_sets["only_in_a"] else None
    divider_after_row_b = len(usable_ids) if id_sets["only_in_b"] else None

    include_ungapped_sites = not args.exclude_ungapped_sites
    image_a = compute_gap_image_rows(
        sequences_a, row_order_a, args.gap_chars, include_ungapped_sites
    )
    image_b = compute_gap_image_rows(
        sequences_b, row_order_b, args.gap_chars, include_ungapped_sites
    )
    plots = [
        {
            "title": "Gap positions",
            "html": render_gap_image_plot(
                image_a,
                image_b,
                name_a,
                name_b,
                divider_after_row_a,
                divider_after_row_b,
                args.gap_image_window_size,
            ),
        },
    ]
    # Whichever of these two Plotly plots is included first embeds the
    # plotly.js library; the other (if also included) reuses it.
    plotly_embedded = False

    if args.include_igcps_plot:
        plots.append(
            {
                "title": "Internal gap count per sequence",
                "html": render_gap_count_scatter_plot(
                    gap_counts, include_plotlyjs=True
                ),
            }
        )
        plotly_embedded = True

    if args.include_pigd_plot:
        diffs = compare_preceding_gap_diffs(
            sequences_a, sequences_b, usable_ids, args.gap_chars
        )
        plots.append(
            {
                "title": "Per-residue internal gap-count difference",
                "html": render_preceding_gap_diff_plot(
                    diffs, include_plotlyjs=not plotly_embedded
                ),
            }
        )

    results["plots"] = plots
    return results


def main(argv: list[str] | None = None) -> None:
    """Entry point for the `alignment-compare` console script."""
    args = parse_args(argv)
    sequences_a, error_a = _try_load(args.file_a)
    sequences_b, error_b = _try_load(args.file_b)

    if error_a is not None or error_b is not None:
        messages = []
        if error_a is not None:
            messages.append(f"A ({args.file_a}): {error_a}")
        if error_b is not None:
            messages.append(f"B ({args.file_b}): {error_b}")
        results = {
            "name_a": args.file_a,
            "name_b": args.file_b,
            "load_error": {"message": " | ".join(messages)},
        }
    else:
        assert sequences_a is not None
        assert sequences_b is not None

        validation_errors = []
        for sequences, label in ((sequences_a, "A"), (sequences_b, "B")):
            try:
                _validate_alignment(sequences, label)
            except InvalidAlignmentError as error:
                validation_errors.append(str(error))
        if validation_errors:
            for message in validation_errors:
                print(f"error: {message}", file=sys.stderr)
            sys.exit(1)

        name_a, name_b = shortest_distinguishing_labels(args.file_a, args.file_b)
        full_path_a = str(Path(args.file_a).resolve())
        full_path_b = str(Path(args.file_b).resolve())
        results = build_results(
            name_a, name_b, full_path_a, full_path_b, sequences_a, sequences_b, args
        )

    html_report = render_compare_report(results)
    Path(args.output).write_text(html_report)
    print(f"Wrote report to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
