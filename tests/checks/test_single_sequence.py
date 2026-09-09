import pytest

from alignment_check.checks.single_sequence import check_single_sequence
from alignment_check.sequence import Sequence


@pytest.mark.parametrize(
    "sequences,expected",
    [
        ([Sequence(id="a", seq="ACGT")], True),
        ([], False),
        (
            [Sequence(id="a", seq="ACGT"), Sequence(id="b", seq="ACGA")],
            False,
        ),
    ],
)
def test_check_single_sequence(
    sequences: list[Sequence], expected: bool
) -> None:
    result = check_single_sequence(sequences)
    assert result["single"] is expected
    assert result["count"] == len(sequences)
