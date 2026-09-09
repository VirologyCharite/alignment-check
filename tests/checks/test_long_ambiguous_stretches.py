from alignment_check.checks.long_ambiguous_stretches import (
    AmbiguousRun,
    check_long_ambiguous_stretches,
    longest_ambiguous_run,
)
from alignment_check.sequence import Sequence


def test_longest_ambiguous_run_finds_the_longest_run() -> None:
    # Runs of length 2 ("NN") and 3 ("RYS") separated by clean bases.
    run = longest_ambiguous_run("ACNNGTRYSAC")
    assert run == AmbiguousRun(start=6, length=3)


def test_longest_ambiguous_run_no_ambiguous_characters() -> None:
    assert longest_ambiguous_run("ACGT") == AmbiguousRun(start=0, length=0)


def test_check_long_ambiguous_stretches_flags_a_long_run() -> None:
    # 4 out of 10 characters ambiguous, above the 30% threshold used here.
    sequences = [Sequence(id="a", seq="ACGTNNNNAC")]
    result = check_long_ambiguous_stretches(sequences, min_length_fraction=0.3)
    assert result["flagged"] == {"a": AmbiguousRun(start=4, length=4)}


def test_check_long_ambiguous_stretches_passes_short_run() -> None:
    sequences = [Sequence(id="a", seq="ACGTNNNNAC")]
    result = check_long_ambiguous_stretches(sequences, min_length_fraction=0.5)
    assert result["flagged"] == {}


def test_check_long_ambiguous_stretches_excludes_given_ids() -> None:
    sequences = [Sequence(id="a", seq="ACGTNNNNAC")]
    result = check_long_ambiguous_stretches(
        sequences, exclude_ids=frozenset({"a"}), min_length_fraction=0.3
    )
    assert result["flagged"] == {}
