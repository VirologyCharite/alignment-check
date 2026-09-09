from alignment_check.checks.indel_regions import IndelRegion, find_indel_regions
from alignment_check.sequence import Sequence


def _wildtype_and_minority_deletion() -> list[Sequence]:
    wildtype = "ACGTACGTAC"
    minority = "AC-----TAC"  # gap at columns 2-6
    sequences = [Sequence(id=f"w{i}", seq=wildtype) for i in range(9)]
    sequences.append(Sequence(id="m0", seq=minority))
    return sequences


def test_find_indel_regions_detects_minority_deletion() -> None:
    sequences = _wildtype_and_minority_deletion()
    regions = find_indel_regions(sequences, minority_fraction=0.2, min_length=5)
    assert regions == [
        IndelRegion(
            start=2, end=6, length=5, minority_ids=["m0"], kind="deletion"
        )
    ]


def test_find_indel_regions_detects_minority_insertion() -> None:
    majority_gapped = "AC-----TAC"
    minority_inserted = "ACGTACGTAC"
    sequences = [Sequence(id=f"w{i}", seq=majority_gapped) for i in range(9)]
    sequences.append(Sequence(id="m0", seq=minority_inserted))

    regions = find_indel_regions(sequences, minority_fraction=0.2, min_length=5)
    assert regions == [
        IndelRegion(
            start=2, end=6, length=5, minority_ids=["m0"], kind="insertion"
        )
    ]


def test_find_indel_regions_below_min_length_is_not_reported() -> None:
    sequences = _wildtype_and_minority_deletion()
    # The gap run is 5 columns long; require 6 to not qualify.
    regions = find_indel_regions(sequences, minority_fraction=0.2, min_length=6)
    assert regions == []


def test_find_indel_regions_above_minority_fraction_is_not_reported() -> None:
    sequences = _wildtype_and_minority_deletion()
    # 1/10 = 0.1, which is not strictly less than 0.1.
    regions = find_indel_regions(sequences, minority_fraction=0.1, min_length=5)
    assert regions == []


def test_find_indel_regions_empty_alignment() -> None:
    assert find_indel_regions([]) == []
