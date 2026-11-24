# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Time-budget conservation, daily cap and availability (protocol section 8)."""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from streak.metrics import learner_arm_metrics
from streak.params import ARMS, ModelParams, get_arm
from streak.population import generate_learners
from streak.simulate import simulate_arm


@settings(max_examples=60, deadline=None)
@given(seed=st.integers(9001, 9999), q=st.floats(0.0, 1.0), cap=st.integers(1, 40),
       arm=st.sampled_from(sorted(ARMS)), form=st.sampled_from(["exponential", "power"]),
       gain=st.sampled_from(["difficulty", "flat"]), h0=st.floats(0.2, 5.0))
def test_conservation_cap_availability(seed, q, cap, arm, form, gain, h0):
    p = ModelParams(n_items=20, horizon_days=28, budget_slots=168, daily_cap_slots=cap, q=q,
                    form=form, gain_rule=gain, h0=h0)
    lr = generate_learners(seed, 1, p)[0]
    res = simulate_arm(lr.initial_half_lives(p), lr.availability(p), lr.outcome_u, get_arm(arm), p)
    spent = int(res.daily_spent.sum())
    m_total = 0 if arm == "A0" else p.budget_slots
    assert spent + res.residual == m_total  # conservation
    assert res.daily_spent.max() <= min(cap, p.n_items)  # daily cap and one review per item per day
    assert np.all(res.daily_spent[~res.available] == 0)  # no practice on unavailable days
    assert res.review_day.size == spent  # one slot per review
    m = learner_arm_metrics(res, p)
    assert m["minutes_spent"] == spent * p.slot_minutes
    assert m["active_days"] + m["missed_available_days"] + m["missed_unavailable_days"] == p.horizon_days
    assert m["longest_streak"] <= m["active_days"]
    assert 0 <= m["R30"] <= 1 and 0 <= m["weakest_decile_R30"] <= m["R30"] + 1e-12


def test_full_availability_zero_residual_default():
    p = ModelParams(q=1.0)
    lr = generate_learners(9001, 1, p)[0]
    for arm in ["A1", "A2", "A3"]:
        res = simulate_arm(lr.initial_half_lives(p), lr.availability(p), lr.outcome_u, get_arm(arm), p)
        assert res.residual == 0 and res.daily_spent.sum() == 672


def test_unavailable_last_days_leave_residual():
    p = ModelParams(n_items=10, horizon_days=14, budget_slots=42, daily_cap_slots=5)
    avail = np.ones(15, dtype=bool)
    avail[0] = False
    avail[12:] = False
    lr = generate_learners(9001, 1, p)[0]
    res = simulate_arm(lr.initial_half_lives(p), avail, lr.outcome_u, get_arm("A2"), p)
    assert res.residual == 3 * 3  # 3 slots per day planned on days 12, 13, 14
    assert res.daily_spent.sum() + res.residual == 42
