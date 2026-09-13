from alignment_check.compare.path_labels import shortest_distinguishing_labels


def test_different_basenames_use_just_the_basename() -> None:
    labels = shortest_distinguishing_labels(
        "/data/run1/alignment1.fasta", "/data/run2/alignment2.fasta"
    )
    assert labels == ("alignment1.fasta", "alignment2.fasta")


def test_same_basename_different_parent_adds_one_component() -> None:
    labels = shortest_distinguishing_labels(
        "/data/run1/alignment.fasta", "/data/run2/alignment.fasta"
    )
    assert labels == ("run1/alignment.fasta", "run2/alignment.fasta")


def test_same_basename_and_parent_adds_further_components() -> None:
    labels = shortest_distinguishing_labels(
        "/data/2024/run/alignment.fasta", "/data/2025/run/alignment.fasta"
    )
    assert labels == ("2024/run/alignment.fasta", "2025/run/alignment.fasta")


def test_identical_paths_return_the_path_unchanged() -> None:
    labels = shortest_distinguishing_labels(
        "/data/run/alignment.fasta", "/data/run/alignment.fasta"
    )
    assert labels == ("/data/run/alignment.fasta", "/data/run/alignment.fasta")


def test_one_path_is_a_suffix_of_the_other() -> None:
    labels = shortest_distinguishing_labels("run/alignment.fasta", "alignment.fasta")
    assert labels == ("run/alignment.fasta", "alignment.fasta")
