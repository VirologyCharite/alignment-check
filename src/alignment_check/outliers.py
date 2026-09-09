"""Shared statistical/fixed-threshold outlier detection.

Used by the per-sequence anomaly checks (GC content, gap count, N count,
ambiguous-code count) to flag sequences with suspiciously low or high
values of some metric. By default, thresholds are derived from the
metric's own mean and standard deviation across the alignment; either
side can be pinned to a fixed value instead.
"""

import statistics
from dataclasses import dataclass

DEFAULT_N_STD_DEVS = 2.0


@dataclass(frozen=True)
class OutlierResult:
    """Which sequences were flagged, and the thresholds that were used.

    Attributes:
        low_ids: IDs of sequences whose value was below `low_threshold`.
        high_ids: IDs of sequences whose value was above `high_threshold`.
        low_threshold: The threshold used for flagging low values.
        high_threshold: The threshold used for flagging high values.
    """

    low_ids: list[str]
    high_ids: list[str]
    low_threshold: float
    high_threshold: float


def detect_outliers(
    values: dict[str, float],
    low_threshold: float | None = None,
    high_threshold: float | None = None,
    n_std_devs: float = DEFAULT_N_STD_DEVS,
) -> OutlierResult:
    """Flag sequences whose metric value is suspiciously low or high.

    Args:
        values: Maps sequence ID to its value for the metric being
            checked (e.g. GC content).
        low_threshold: A fixed lower threshold. If None (the default),
            the threshold is `mean - n_std_devs * stdev` of `values`.
        high_threshold: A fixed upper threshold. If None (the default),
            the threshold is `mean + n_std_devs * stdev` of `values`.
        n_std_devs: How many standard deviations from the mean counts as
            an outlier, when a threshold is not fixed.

    Returns:
        An `OutlierResult` listing the flagged sequence IDs (sorted) and
        the thresholds that were applied.

    Raises:
        ValueError: If `values` is empty and a threshold was not fixed
            (there is no distribution to derive it from).
    """
    if low_threshold is None or high_threshold is None:
        if not values:
            raise ValueError(
                "Cannot derive a statistical threshold from no values."
            )
        sample = list(values.values())
        mean = statistics.mean(sample)
        stdev = statistics.stdev(sample) if len(sample) > 1 else 0.0
        if low_threshold is None:
            low_threshold = mean - n_std_devs * stdev
        if high_threshold is None:
            high_threshold = mean + n_std_devs * stdev

    low_ids = sorted(id_ for id_, value in values.items() if value < low_threshold)
    high_ids = sorted(id_ for id_, value in values.items() if value > high_threshold)

    return OutlierResult(low_ids, high_ids, low_threshold, high_threshold)
