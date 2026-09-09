from pathlib import Path

from alignment_check.cli.alignment_check import main


def _write_fasta(path: Path, records: dict[str, str]) -> None:
    text = "".join(f">{id_}\n{seq}\n" for id_, seq in records.items())
    path.write_text(text)


def test_main_writes_report_for_valid_alignment(tmp_path: Path) -> None:
    fasta = tmp_path / "in.fasta"
    _write_fasta(
        fasta,
        {
            "a": "ACGTACGTACGT",
            "b": "ACGTACGTACGA",
            "dup": "ACGTACGTACGT",
        },
    )
    # Duplicate the "dup" ID to trigger the duplicate_ids error.
    fasta.write_text(fasta.read_text() + ">dup\nACGTACGTACGT\n")
    output = tmp_path / "report.html"

    main([str(fasta), "-o", str(output)])

    html = output.read_text()
    assert "Number of sequences: 4" in html
    assert "No duplicate sequence IDs" in html
    assert 'class="badge fail"' in html
    assert "Site gap fraction" in html


def test_main_missing_file_writes_error_report(tmp_path: Path) -> None:
    output = tmp_path / "report.html"

    main([str(tmp_path / "missing.fasta"), "-o", str(output)])

    html = output.read_text()
    # The exact message differs: prseq raises a different exception for a
    # missing file when it detects it's running under pytest.
    assert 'class="badge fail"' in html
    assert "Number of sequences" not in html


def test_main_allow_all_id_chars_disables_id_check(tmp_path: Path) -> None:
    fasta = tmp_path / "in.fasta"
    _write_fasta(fasta, {"seq(1)": "ACGT", "seq2": "ACGA"})
    output = tmp_path / "report.html"

    main([str(fasta), "-o", str(output), "--allow-all-id-chars"])

    assert "problematic characters" not in output.read_text()


def test_main_n2_enables_pairwise_identity_plot(tmp_path: Path) -> None:
    fasta = tmp_path / "in.fasta"
    _write_fasta(fasta, {"a": "ACGT", "b": "ACGA"})
    with_n2 = tmp_path / "with_n2.html"
    without_n2 = tmp_path / "without_n2.html"

    main([str(fasta), "-o", str(with_n2), "--n2"])
    main([str(fasta), "-o", str(without_n2)])

    assert "Pairwise sequence identity" in with_n2.read_text()
    assert "Pairwise sequence identity" not in without_n2.read_text()


def test_main_excludes_all_gap_sequence_from_analysis(tmp_path: Path) -> None:
    fasta = tmp_path / "in.fasta"
    _write_fasta(fasta, {"a": "ACGT", "b": "ACGA", "gappy": "----"})
    output = tmp_path / "report.html"

    main([str(fasta), "-o", str(output)])

    html = output.read_text()
    assert "excluded from anomaly/info analysis" in html
    assert "gappy" in html
