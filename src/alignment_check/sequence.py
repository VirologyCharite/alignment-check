"""The basic data type shared by every check and info function."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sequence:
    """One sequence (a row) from a multiple sequence alignment.

    Attributes:
        id: The sequence identifier, taken from the FASTA header line
            (without the leading '>').
        seq: The sequence data, exactly as read from the input file
            (not upper-cased or otherwise normalized).
    """

    id: str
    seq: str
