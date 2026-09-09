from pathlib import Path

import pytest

from alignment_check.exceptions import AlignmentFileNotFoundError, NotFastaError
from alignment_check.loader import load_sequences
from alignment_check.sequence import Sequence


def test_load_sequences_reads_fasta_file(tmp_path: Path) -> None:
    fasta = tmp_path / "valid.fasta"
    fasta.write_text(">seq1\nACGT\n>seq2\nACGA\n")

    assert load_sequences(str(fasta)) == [
        Sequence(id="seq1", seq="ACGT"),
        Sequence(id="seq2", seq="ACGA"),
    ]


def test_load_sequences_empty_file_returns_empty_list(tmp_path: Path) -> None:
    fasta = tmp_path / "empty.fasta"
    fasta.write_text("")

    assert load_sequences(str(fasta)) == []


def test_load_sequences_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.fasta"

    with pytest.raises(AlignmentFileNotFoundError):
        load_sequences(str(missing))


def test_load_sequences_non_fasta_file_raises(tmp_path: Path) -> None:
    not_fasta = tmp_path / "not_fasta.txt"
    not_fasta.write_text("this is not fasta\n")

    with pytest.raises(NotFastaError):
        load_sequences(str(not_fasta))
