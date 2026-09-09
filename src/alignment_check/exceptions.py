"""Exceptions raised while loading an alignment, before any sequence-level
checks can run.
"""


class AlignmentFileNotFoundError(Exception):
    """Raised when the given input file does not exist."""


class NotFastaError(Exception):
    """Raised when the input does not look like valid FASTA."""
