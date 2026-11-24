# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Synthetic learner generation: determinism and common random numbers."""

import numpy as np
import pytest

from streak.params import ModelParams, ParameterError
from streak.population import generate_learners


def test_deterministic():
    p = ModelParams()
    a, b = generate_learners(9001, 3, p), generate_learners(9001, 3, p)
    for x, y in zip(a, b):
        assert np.array_equal(x.z_items, y.z_items) and np.array_equal(x.outcome_u, y.outcome_u)


def test_learner_independent_of_population_size():
    p = ModelParams()
    assert np.array_equal(generate_learners(9001, 2, p)[1].outcome_u, generate_learners(9001, 50, p)[1].outcome_u)


def test_seeds_differ():
    p = ModelParams()
    assert not np.array_equal(generate_learners(9001, 1, p)[0].z_items, generate_learners(9002, 1, p)[0].z_items)


def test_crn_across_cells():
    lr = generate_learners(9001, 1, ModelParams())[0]
    h1 = lr.initial_half_lives(ModelParams(h0=1.0))
    h2 = lr.initial_half_lives(ModelParams(h0=2.0))
    assert np.allclose(h2, 2 * h1)
    a_lo, a_hi = lr.availability(ModelParams(q=0.7)), lr.availability(ModelParams(q=0.85))
    assert np.all(a_hi[a_lo])  # every day available at q = 0.7 is available at q = 0.85
    assert not lr.availability(ModelParams(q=1.0))[0] and lr.availability(ModelParams(q=1.0))[1:].all()


def test_population_moments_plausible():
    p = ModelParams()
    lrs = generate_learners(9005, 200, p)
    z = np.concatenate([lr.z_items for lr in lrs])
    assert abs(z.mean()) < 0.05 and abs(z.std() - 1) < 0.05
    av = np.concatenate([lr.availability(p)[1:] for lr in lrs])
    assert abs(av.mean() - 0.85) < 0.02


@pytest.mark.parametrize("seed,n", [(-1, 1), (1, 0), ("1", 1)])
def test_invalid(seed, n):
    with pytest.raises(ParameterError):
        generate_learners(seed, n, ModelParams())
