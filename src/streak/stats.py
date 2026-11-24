# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Paired analysis: stratified percentile bootstrap, SESOI classification, Holm,
effect size and Spearman correlation (protocol sections 4 and 6).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


def stratified_bootstrap_means(values: np.ndarray, strata: np.ndarray, resamples: int,
                               seed: int) -> np.ndarray:
    """Bootstrap distribution of the pooled mean, resampling units within each stratum.

    Each replicate draws, for every stratum, as many units as it has (with
    replacement) and returns the mean over all drawn units.
    """
    values = np.asarray(values, dtype=float)
    strata = np.asarray(strata)
    if values.ndim != 1 or values.shape != strata.shape or values.size == 0:
        raise ValueError("values and strata must be non-empty 1-D arrays of equal length")
    if resamples < 1:
        raise ValueError("resamples must be positive")
    if not np.all(np.isfinite(values)):
        raise ValueError("values must be finite")
    rng = np.random.default_rng(seed)
    total = np.zeros(resamples)
    for s in np.unique(strata):
        v = values[strata == s]
        idx = rng.integers(0, v.size, size=(resamples, v.size))
        total += v[idx].sum(axis=1)
    return total / values.size


def percentile_interval(boot: np.ndarray, level: float) -> tuple[float, float]:
    if not 0 < level < 1:
        raise ValueError("level must lie in (0, 1)")
    alpha = 1 - level
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def bootstrap_p_two_sided(boot: np.ndarray, null: float = 0.0) -> float:
    """Two-sided percentile-bootstrap p-value: 2 * min share on either side of null, capped at 1."""
    lo = np.mean(boot <= null)
    hi = np.mean(boot >= null)
    return float(min(1.0, 2 * min(lo, hi)))


def holm_adjust(pvalues: list[float]) -> list[float]:
    """Holm step-down adjusted p-values (monotone, capped at 1)."""
    m = len(pvalues)
    order = np.argsort(pvalues, kind="stable")
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvalues[i])
        adj[i] = min(1.0, running)
    return [float(x) for x in adj]


def classify(ci95: tuple[float, float], ci90: tuple[float, float], sesoi: float) -> str:
    """Decision rule of protocol section 4."""
    lo95, hi95 = ci95
    lo90, hi90 = ci90
    if -sesoi < lo90 and hi90 < sesoi:
        return "practically equivalent under the model"
    if hi95 < -sesoi:
        return "relevant negative"
    if lo95 > sesoi:
        return "relevant positive"
    if hi95 < 0 or lo95 > 0:
        return "detectable but below the SESOI"
    return "inconclusive"


def spearman(x: np.ndarray, y: np.ndarray) -> float | None:
    """Spearman rank correlation with average ranks for ties; None if undefined."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size != y.size or x.size < 3:
        return None
    rx, ry = _avg_rank(x), _avg_rank(y)
    if np.std(rx) == 0 or np.std(ry) == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def _avg_rank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="stable")
    ranks = np.empty(x.size)
    sx = x[order]
    i = 0
    while i < x.size:
        j = i
        while j + 1 < x.size and sx[j + 1] == sx[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


@dataclass
class PairedSummary:
    contrast: str
    metric: str
    n: int
    mean_diff: float
    sd_diff: float
    d_z: float | None
    ci95: tuple[float, float]
    ci90: tuple[float, float]
    p_boot: float
    per_seed_mean: dict[str, float]
    quantiles: dict[str, float]
    classification: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ci95"] = list(self.ci95)
        d["ci90"] = list(self.ci90)
        return d


def paired_summary(diff: np.ndarray, seeds: np.ndarray, contrast: str, metric: str,
                   resamples: int, boot_seed: int, sesoi: float) -> PairedSummary:
    diff = np.asarray(diff, dtype=float)
    boot = stratified_bootstrap_means(diff, seeds, resamples, boot_seed)
    sd = float(np.std(diff, ddof=1)) if diff.size > 1 else 0.0
    ci95 = percentile_interval(boot, 0.95)
    ci90 = percentile_interval(boot, 0.90)
    qs = np.quantile(diff, [0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0])
    per_seed = {str(s): float(diff[seeds == s].mean()) for s in np.unique(seeds)}
    return PairedSummary(
        contrast=contrast, metric=metric, n=int(diff.size), mean_diff=float(diff.mean()),
        sd_diff=sd, d_z=(float(diff.mean()) / sd if sd > 0 else None), ci95=ci95, ci90=ci90,
        p_boot=bootstrap_p_two_sided(boot), per_seed_mean=per_seed,
        quantiles={k: float(v) for k, v in zip(["min", "q05", "q25", "median", "q75", "q95", "max"], qs)},
        classification=classify(ci95, ci90, sesoi),
    )
