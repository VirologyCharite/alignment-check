"""Reads a FASTA alignment file (or standard input) into `Sequence` objects.
"""

import prseq

from alignment_check.exceptions import AlignmentFileNotFoundError, NotFastaError
from alignment_check.sequence import Sequence


def load_sequences(path: str | None) -> list[Sequence]:
    """Read all sequences from a FASTA file, or from standard input.

    Args:
        path: Path to a FASTA file, or None to read from standard input.

    Returns:
        The sequences found in the input, in file order. An empty list is
        returned for an empty (but otherwise valid) input.

    Raises:
        AlignmentFileNotFoundError: If `path` is given but does not exist.
        NotFastaError: If the input cannot be parsed as FASTA.
    """
    try:
        records = list(prseq.FastaReader(path))
    except FileNotFoundError as error:
        # prseq normally raises ValueError for a missing file (handled
        # below), but under pytest it detects the test environment and
        # takes a different code path that raises this instead.
        raise AlignmentFileNotFoundError(str(error)) from error
    except ValueError as error:
        raise AlignmentFileNotFoundError(str(error)) from error
    except OSError as error:
        raise NotFastaError(str(error)) from error

    return [Sequence(id=record.id, seq=record.sequence) for record in records]
