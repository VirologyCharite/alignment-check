import pytest

from alignment_check.outliers import OutlierResult, detect_outliers


def test_detect_outliers_flags_nothing_for_a_tight_cluster() -> None:
    values = {"a": 0.50, "b": 0.51, "c": 0.49, "d": 0.50}
    result = detect_outliers(values)
    assert result.low_ids == []
    assert result.high_ids == []


def test_detect_outliers_flags_statistical_high_outlier() -> None:
    values = {
        "a": 0.48, "b": 0.49, "c": 0.50, "d": 0.50, "e": 0.51, "f": 0.52,
        "g": 0.99,
    }
    result = detect_outliers(values)
    assert result.high_ids == ["g"]
    assert result.low_ids == []


def test_detect_outliers_flags_statistical_low_outlier() -> None:
    values = {
        "a": 0.48, "b": 0.49, "c": 0.50, "d": 0.50, "e": 0.51, "f": 0.52,
        "g": 0.01,
    }
    result = detect_outliers(values)
    assert result.low_ids == ["g"]
    assert result.high_ids == []


@pytest.mark.parametrize(
    "low_threshold,high_threshold,expected_low,expected_high",
    [
        # With only two points spread this far apart, the statistical
        # thresholds fall outside both of them, so nothing is flagged
        # unless a fixed threshold is given for that side.
        (0.2, None, ["a"], []),
        (None, 0.8, [], ["b"]),
        (0.2, 0.8, ["a"], ["b"]),
    ],
)
def test_detect_outliers_fixed_threshold_overrides_statistical(
    low_threshold: float | None,
    high_threshold: float | None,
    expected_low: list[str],
    expected_high: list[str],
) -> None:
    values = {"a": 0.1, "b": 0.9}
    result = detect_outliers(
        values, low_threshold=low_threshold, high_threshold=high_threshold
    )
    assert result.low_ids == expected_low
    assert result.high_ids == expected_high


def test_detect_outliers_empty_values_raises_without_fixed_thresholds() -> None:
    with pytest.raises(ValueError):
        detect_outliers({})


def test_detect_outliers_empty_values_ok_with_fixed_thresholds() -> None:
    result = detect_outliers({}, low_threshold=0.0, high_threshold=1.0)
    assert result == OutlierResult([], [], 0.0, 1.0)


def test_detect_outliers_single_value_has_zero_spread() -> None:
    # With one value, stdev is 0, so the value itself is never an outlier.
    result = detect_outliers({"a": 0.5})
    assert result.low_ids == []
    assert result.high_ids == []
