# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Statistics: bootstrap, Holm, SESOI classification, Spearman."""

import numpy as np
import pytest

from streak.stats import (bootstrap_p_two_sided, classify, holm_adjust, paired_summary,
                          percentile_interval, spearman, stratified_bootstrap_means)


def test_constant_within_strata_gives_exact_mean():
    v = np.array([1.0, 1.0, 1.0, 3.0, 3.0])
    s = np.array([1, 1, 1, 2, 2])
    boot = stratified_bootstrap_means(v, s, 500, 1)
    assert np.allclose(boot, v.mean())  # strata sizes preserved, so the pooled mean is fixed


def test_bootstrap_deterministic_and_centered():
    rng = np.random.default_rng(0)
    v = rng.normal(0.3, 1, 400)
    s = np.repeat([1, 2, 3, 4], 100)
    b1 = stratified_bootstrap_means(v, s, 2000, 7)
    assert np.array_equal(b1, stratified_bootstrap_means(v, s, 2000, 7))
    lo, hi = percentile_interval(b1, 0.95)
    assert lo < v.mean() < hi
    assert hi - lo == pytest.approx(2 * 1.96 / 20, rel=0.2)


def test_bootstrap_invalid():
    with pytest.raises(ValueError):
        stratified_bootstrap_means(np.array([]), np.array([]), 10, 0)
    with pytest.raises(ValueError):
        stratified_bootstrap_means(np.array([1.0, np.nan]), np.array([1, 1]), 10, 0)
    with pytest.raises(ValueError):
        percentile_interval(np.zeros(3), 1.5)


def test_holm_golden():
    assert holm_adjust([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm_adjust([0.5, 0.9]) == pytest.approx([1.0, 1.0])


def test_p_value():
    assert bootstrap_p_two_sided(np.array([1.0, 2.0, 3.0])) == 0.0
    assert bootstrap_p_two_sided(np.array([-1.0, 1.0])) == 1.0


@pytest.mark.parametrize("ci95,ci90,expected", [
    ((-0.05, -0.03), (-0.045, -0.035), "relevant negative"),
    ((0.03, 0.05), (0.035, 0.045), "relevant positive"),
    ((-0.01, 0.01), (-0.008, 0.008), "practically equivalent under the model"),
    ((-0.03, -0.001), (-0.025, -0.005), "detectable but below the SESOI"),
    ((-0.03, 0.01), (-0.025, 0.005), "inconclusive"),
])
def test_classify(ci95, ci90, expected):
    assert classify(ci95, ci90, 0.02) == expected


def test_spearman():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    # Ties: x ranks [1.5, 1.5, 3, 4], y ranks [1, 2, 3, 4]; Pearson of ranks = 0.9486833.
    assert spearman([1, 1, 2, 3], [1, 2, 3, 4]) == pytest.approx(0.9486833, rel=1e-6)
    assert spearman([1, 1, 1], [1, 2, 3]) is None
    assert spearman([1, 2], [1, 2]) is None


def test_paired_summary_fields():
    d = np.array([0.1, 0.2, 0.3, 0.4])
    s = paired_summary(d, np.array([1, 1, 2, 2]), "X - Y", "R30", 300, 3, 0.02)
    assert s.mean_diff == pytest.approx(0.25) and s.n == 4
    assert s.per_seed_mean == {"1": pytest.approx(0.15), "2": pytest.approx(0.35)}
    assert s.classification == "relevant positive"
