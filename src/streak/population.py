# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Synthetic learner generation (the project's only "ingestion": no external data).

Each learner is generated from a NumPy SeedSequence child of its master seed, so
that learner j of master seed m is identical in every arm, in every grid cell
and in every model variant (common random numbers). Random draws are stored as
parameter-free base variates; cell parameters (h0, q) are applied afterwards.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .params import ModelParams, ParameterError

#: Development and smoke seeds; never pooled with confirmatory results.
SMOKE_SEED_RANGE = range(9001, 10000)


@dataclass(frozen=True)
class LearnerDraws:
    """Parameter-free random draws for one learner.

    z_learner: standard normal for learner ability (theta = exp(sigma_learner * z)).
    z_items: K standard normals for item difficulty (u_i = exp(sigma_item * z_i)).
    avail_u: uniforms for days 0..T; day d is available iff avail_u[d] < q (index 0 unused).
    outcome_u: (T + 1, K) uniforms; a review of item i on day d succeeds iff
        outcome_u[d, i] < p, so the same (day, item) review has the same outcome
        draw in every arm.
    """

    master_seed: int
    learner_index: int
    z_learner: float
    z_items: np.ndarray
    avail_u: np.ndarray
    outcome_u: np.ndarray

    def initial_half_lives(self, p: ModelParams) -> np.ndarray:
        """h_i = h0 * u_i * theta_l (days)."""
        theta = np.exp(p.sigma_learner * self.z_learner)
        u = np.exp(p.sigma_item * self.z_items)
        return p.h0 * u * theta

    def availability(self, p: ModelParams) -> np.ndarray:
        """Boolean array of length T + 1; index 0 (initial study day) is False."""
        av = self.avail_u < p.q
        av[0] = False
        return av


def generate_learners(master_seed: int, n_learners: int, p: ModelParams) -> list[LearnerDraws]:
    """Generate ``n_learners`` learners for one master seed. Deterministic."""
    if not isinstance(master_seed, int) or master_seed < 0:
        raise ParameterError(f"master_seed must be a non-negative integer, got {master_seed!r}")
    if not isinstance(n_learners, int) or n_learners < 1:
        raise ParameterError(f"n_learners must be a positive integer, got {n_learners!r}")
    root = np.random.SeedSequence(master_seed)
    out = []
    for j, child in enumerate(root.spawn(n_learners)):
        s_ability, s_avail, s_outcome = child.spawn(3)
        r_ability = np.random.default_rng(s_ability)
        z_learner = float(r_ability.standard_normal())
        z_items = r_ability.standard_normal(p.n_items)
        avail_u = np.random.default_rng(s_avail).random(p.horizon_days + 1)
        outcome_u = np.random.default_rng(s_outcome).random((p.horizon_days + 1, p.n_items))
        out.append(LearnerDraws(master_seed, j, z_learner, z_items, avail_u, outcome_u))
    return out
