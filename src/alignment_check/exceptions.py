"""Exceptions raised when an input can't be treated as an alignment at
all -- either because it couldn't be loaded, or because, once loaded,
it fails a basic structural precondition (e.g. its sequences aren't all
the same length) that later processing assumes holds.
"""


class AlignmentFileNotFoundError(Exception):
    """Raised when the given input file does not exist."""


class NotFastaError(Exception):
    """Raised when the input does not look like valid FASTA."""


class InvalidAlignmentError(Exception):
    """Raised when a loaded alignment fails a basic validity check (e.g.
    it's empty, or its sequences aren't all the same length).
    """
