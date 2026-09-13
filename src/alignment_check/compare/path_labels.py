"""Builds short, human-friendly labels for two file paths.

Used so a report can refer to "A" and "B" by something more meaningful
than a letter, and more concise than the full path, without the two
labels colliding.
"""

from pathlib import Path


def shortest_distinguishing_labels(path_a: str, path_b: str) -> tuple[str, str]:
    """Find the shortest trailing path components that tell two paths apart.

    Starting from just the basename, more path components are added from
    the right until the two paths differ. If the paths never differ
    (they're identical, or one's parts are a suffix of the other's all
    the way to the top), each path is returned in full.

    Args:
        path_a: The first path.
        path_b: The second path.

    Returns:
        A (label_a, label_b) pair: the shortest matching-length trailing
        slice of each path that distinguishes it from the other.
    """
    parts_a = Path(path_a).parts
    parts_b = Path(path_b).parts
    max_components = max(len(parts_a), len(parts_b))

    for num_components in range(1, max_components + 1):
        suffix_a = parts_a[-num_components:]
        suffix_b = parts_b[-num_components:]
        if suffix_a != suffix_b:
            return str(Path(*suffix_a)), str(Path(*suffix_b))

    return path_a, path_b
