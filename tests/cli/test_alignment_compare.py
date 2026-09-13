from pathlib import Path

import pytest

from alignment_check.cli.alignment_compare import main


def _write_fasta(path: Path, records: dict[str, str]) -> None:
    text = "".join(f">{id_}\n{seq}\n" for id_, seq in records.items())
    path.write_text(text)


def test_main_writes_report_for_two_valid_alignments(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "--AC-GT-", "s2": "ACGTACGT"})
    _write_fasta(file_b, {"s1": "AC--GT--", "s2": "ACGTACGT"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert "Number of sequences: A=2, B=2" in html
    assert "Same sequence IDs (2 in common)" in html
    assert "Gap positions" in html
    # Off by default.
    assert "Internal gap count per sequence" not in html
    assert "Per-residue internal gap-count difference" not in html
    assert "<td>s1</td>" in html
    assert f"A: {file_a.resolve()} (a.fasta)" in html
    assert f"B: {file_b.resolve()} (b.fasta)" in html


def test_main_include_igcps_and_pigd_plot_flags(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "--AC-GT-", "s2": "ACGTACGT"})
    _write_fasta(file_b, {"s1": "AC--GT--", "s2": "ACGTACGT"})
    output = tmp_path / "report.html"

    main(
        [
            str(file_a),
            str(file_b),
            "-o",
            str(output),
            "--include-igcps-plot",
            "--include-pigd-plot",
        ]
    )

    html = output.read_text()
    assert "Internal gap count per sequence" in html
    assert "Per-residue internal gap-count difference" in html


def test_main_include_pigd_plot_alone_still_embeds_plotlyjs(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "--AC-GT"})
    _write_fasta(file_b, {"s1": "AC--GT"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output), "--include-pigd-plot"])

    html = output.read_text()
    assert "Per-residue internal gap-count difference" in html
    assert "Plotly.newPlot" in html


def test_main_uses_shortest_distinguishing_label_for_same_basename(
    tmp_path: Path,
) -> None:
    dir_a = tmp_path / "run1"
    dir_b = tmp_path / "run2"
    dir_a.mkdir()
    dir_b.mkdir()
    file_a = dir_a / "aln.fasta"
    file_b = dir_b / "aln.fasta"
    _write_fasta(file_a, {"s1": "ACGT"})
    _write_fasta(file_b, {"s1": "ACGT"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert f"A: {file_a.resolve()} (run1/aln.fasta)" in html
    assert f"B: {file_b.resolve()} (run2/aln.fasta)" in html


def test_main_reports_ids_only_in_one_file(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "ACGT", "only_a": "ACGT"})
    _write_fasta(file_b, {"s1": "ACGT", "only_b": "ACGT"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert "only_a" in html
    assert "only_b" in html
    assert 'class="badge fail"' in html
    # The gap-position images should show the unique-to-one-file
    # sequences below a divider, not silently drop them.
    assert "1 common sequences, 1 unique to this file" in html


def test_main_no_divider_shown_when_sequence_sets_match(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "ACGT"})
    _write_fasta(file_b, {"s1": "ACGT"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    assert "unique to this file" not in output.read_text()


def test_main_flags_mismatched_content_and_excludes_from_tier2(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "ACGT"})
    _write_fasta(file_b, {"s1": "ACGA"})  # different ungapped content
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert "No further comparison performed" in html
    assert "Gap positions" not in html


def test_main_missing_file_writes_error_report(tmp_path: Path) -> None:
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_b, {"s1": "ACGT"})
    output = tmp_path / "report.html"

    main([str(tmp_path / "missing.fasta"), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert 'class="badge fail"' in html
    assert "Basic comparison" not in html


def test_main_reports_width_and_difference(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "A" * 10})
    _write_fasta(file_b, {"s1": "A" * 8})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert "Alignment width: A=10, B=8 (difference: +2)" in html


def test_main_exits_with_error_when_a_files_lengths_are_inconsistent(
    tmp_path: Path,
) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    # file_a's own sequences aren't even the same length as each other,
    # which every later computation assumes -- this must be rejected
    # up front rather than crash partway through.
    _write_fasta(file_a, {"s1": "AAAAAAA", "s2": "AAAAAAAA"})
    _write_fasta(file_b, {"s1": "AAAAAAAA", "s2": "AAAAAAAA"})
    output = tmp_path / "report.html"

    with pytest.raises(SystemExit) as excinfo:
        main([str(file_a), str(file_b), "-o", str(output)])

    assert excinfo.value.code == 1
    assert not output.exists()


def test_main_exits_with_error_for_empty_alignment(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    file_a.write_text("")
    _write_fasta(file_b, {"s1": "ACGT"})
    output = tmp_path / "report.html"

    with pytest.raises(SystemExit) as excinfo:
        main([str(file_a), str(file_b), "-o", str(output)])

    assert excinfo.value.code == 1
    assert not output.exists()


def test_main_reports_both_files_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "AAA", "s2": "AAAA"})
    file_b.write_text("")
    output = tmp_path / "report.html"

    with pytest.raises(SystemExit):
        main([str(file_a), str(file_b), "-o", str(output)])

    stderr = capsys.readouterr().err
    assert "A's sequences are not all the same length" in stderr
    assert "B contains no sequences" in stderr
    assert not output.exists()


def test_main_identical_files(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "AC-GT"})
    _write_fasta(file_b, {"s1": "AC-GT"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    assert "The two files are identical." in output.read_text()


def test_main_default_shows_every_column_with_a_ruler(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "--AC-GT"})
    _write_fasta(file_b, {"s1": "AC--GT"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert "7 of 7 columns shown" in html
    assert 'class="gap-image-ruler"' in html


def test_main_exclude_ungapped_sites_compresses_and_drops_ruler(
    tmp_path: Path,
) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    # Two non-adjacent gaps in each, so the compressed columns are
    # non-contiguous (0,1 and 3,4 aren't next to each other) for both.
    _write_fasta(file_a, {"s1": "A-C-GT"})
    _write_fasta(file_b, {"s1": "AC-G-T"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output), "--exclude-ungapped-sites"])

    html = output.read_text()
    assert "2 of 6 columns shown" in html
    assert 'class="gap-image-ruler"' not in html


def test_main_flags_gap_only_column(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    # Column 2 (0-based) is a gap in every sequence of file A.
    _write_fasta(file_a, {"s1": "AC-GT", "s2": "AC-GA"})
    _write_fasta(file_b, {"s1": "ACGT", "s2": "ACGA"})
    output = tmp_path / "report.html"

    main([str(file_a), str(file_b), "-o", str(output)])

    html = output.read_text()
    assert "No gap-only columns in A" in html
    assert "No gap-only columns in B" in html
    assert "1 column(s): [2]" in html




def test_main_gap_image_window_size_splits_into_chunks(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "ACGTACGTAC"})
    _write_fasta(file_b, {"s1": "ACGTACGTAC"})
    output = tmp_path / "report.html"

    main(
        [
            str(file_a),
            str(file_b),
            "-o",
            str(output),
            "--gap-image-window-size",
            "4",
        ]
    )

    html = output.read_text()
    # 10 columns / window 4 -> 3 chunks.
    assert html.count('class="gap-image-chunk"') == 3
    assert "(chunk 1 of 3)" in html


def test_main_gap_image_window_size_must_be_positive(tmp_path: Path) -> None:
    file_a = tmp_path / "a.fasta"
    file_b = tmp_path / "b.fasta"
    _write_fasta(file_a, {"s1": "ACGT"})
    _write_fasta(file_b, {"s1": "ACGT"})

    with pytest.raises(SystemExit):
        main(
            [
                str(file_a),
                str(file_b),
                "--gap-image-window-size",
                "0",
            ]
        )
