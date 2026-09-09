import math

from alignment_check.info.pairwise_identity import default_identity


def test_default_identity_all_match() -> None:
    assert default_identity("ACGT", "ACGT") == 1.0


def test_default_identity_partial_match() -> None:
    assert default_identity("ACGT", "ACGA") == 0.75


def test_default_identity_gap_vs_base_is_mismatch() -> None:
    assert default_identity("AC-T", "ACGT") == 0.75


def test_default_identity_gap_vs_gap_is_ignored() -> None:
    # Column 2 is gap-vs-gap and doesn't count toward the denominator.
    assert default_identity("AC-T", "AC-A") == 2 / 3


def test_default_identity_no_comparable_columns_is_nan() -> None:
    assert math.isnan(default_identity("--", "--"))
