# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""No-practice control and hand-computed golden examples (protocol section 8)."""

import numpy as np
import pytest

from streak.metrics import learner_arm_metrics
from streak.params import ModelParams, get_arm
from streak.population import generate_learners
from streak.simulate import simulate_arm

UPD = dict(g_min=0.1, a=2.5)


@pytest.mark.parametrize("form", ["exponential", "power"])
def test_no_practice_control_closed_form(form):
    p = ModelParams(form=form)
    lr = generate_learners(9001, 1, p)[0]
    h = lr.initial_half_lives(p)
    res = simulate_arm(h, lr.availability(p), lr.outcome_u, get_arm("A0"), p)
    m = learner_arm_metrics(res, p)
    t = p.horizon_days + 30
    expected = np.mean(2.0 ** (-t / h)) if form == "exponential" else np.mean((1 + 3 * t / h) ** -0.5)
    assert m["R30"] == pytest.approx(expected, rel=1e-12)
    assert m["reviews"] == m["slots_spent"] == m["minutes_spent"] == m["active_days"] == 0
    assert m["residual_slots"] == 0 and m["item_coverage"] == 0 and m["practice_success_rate"] is None
    assert np.array_equal(res.half_life, h)


def _tiny(t_days=2, m=2):
    return ModelParams(n_items=2, horizon_days=t_days, budget_slots=m, retention_delays=(1, 30))


def test_golden_round_robin_all_success():
    p = _tiny()
    h_init = np.array([1.0, 2.0])
    avail = np.array([False, True, True])
    res = simulate_arm(h_init, avail, np.zeros((3, 2)), get_arm("D-RR"), p)
    # Day 1: item 0, delay 1, p = 2^(-1/1) = 0.5, h = 1 * (1 + 0.1 + 2.5 * 0.5) = 2.35.
    # Day 2: item 1, delay 2, p = 2^(-2/2) = 0.5, h = 2 * 2.35 = 4.7.
    assert list(res.review_item) == [0, 1]
    assert res.half_life == pytest.approx([2.35, 4.7])
    assert res.last_review == pytest.approx([1, 2])
    m = learner_arm_metrics(res, p)
    r30 = (2 ** (-31 / 2.35) + 2 ** (-30 / 4.7)) / 2  # t = T + 30 = 32
    assert m["R30"] == pytest.approx(r30)
    assert m["R30"] == pytest.approx(0.0060445, abs=1e-6)  # closed form evaluated separately: (0.0001069 + 0.0119821) / 2
    assert m["practice_success_rate"] == 1.0 and m["longest_streak"] == 2 and m["final_streak"] == 2


def test_golden_round_robin_all_fail():
    p = _tiny()
    res = simulate_arm(np.array([1.0, 2.0]), np.array([False, True, True]), np.ones((3, 2)), get_arm("D-RR"), p)
    assert res.half_life == pytest.approx([0.6, 1.2])  # max(0.25, 0.6 h)
    assert learner_arm_metrics(res, p)["practice_success_rate"] == 0.0


def test_golden_easiest_and_most_due():
    p = _tiny()
    h_init = np.array([1.0, 2.0])
    avail = np.array([False, True, True])
    u = np.zeros((3, 2))
    # Day 1: beliefs equal (h_hat = h0 = 1), tie -> item 0 for both rules; true h0 becomes 2.35,
    # belief of item 0 becomes 2.35. Day 2: belief p_hat = [2^(-1/2.35), 2^(-2/1)] = [0.745, 0.25].
    a2 = simulate_arm(h_init, avail, u, get_arm("A2"), p)
    assert list(a2.review_item) == [0, 0]
    p2 = 2 ** (-1 / 2.35)
    assert a2.half_life == pytest.approx([2.35 * (1.1 + 2.5 * (1 - p2)), 2.0])
    a3 = simulate_arm(h_init, avail, u, get_arm("A3"), p)
    assert list(a3.review_item) == [0, 1]
    assert a3.half_life == pytest.approx([2.35, 4.7])


def test_golden_fixed_makeup_and_cap():
    p = ModelParams(n_items=4, horizon_days=7, budget_slots=3, daily_cap_slots=60)
    h = np.ones(4)
    u = np.zeros((8, 4))
    avail = np.array([False, True, True, False, True, True, True, True])
    res = simulate_arm(h, avail, u, get_arm("A1"), p)
    # Sessions on days 1, 3, 5 (1 slot each); day 3 unavailable -> make-up on day 4.
    assert list(res.daily_spent) == [0, 1, 0, 0, 1, 1, 0, 0]
    p_cap = ModelParams(n_items=4, horizon_days=7, budget_slots=3, daily_cap_slots=1)
    avail2 = np.array([False, True, True, False, False, True, True, True])
    res2 = simulate_arm(h, avail2, u, get_arm("A1"), p_cap)
    # Day 5 owes 2 slots but the cap is 1; the remaining slot moves to day 6.
    assert list(res2.daily_spent) == [0, 1, 0, 0, 0, 1, 1, 0]
    assert res2.residual == 0


def test_streak_metrics_golden():
    from streak.metrics import runs_of_true
    assert runs_of_true(np.array([1, 1, 0, 1, 1, 1, 0], bool)) == (3, 0)
    assert runs_of_true(np.array([0, 1, 1], bool)) == (2, 2)
    assert runs_of_true(np.array([], bool)) == (0, 0)


def test_invalid_simulation_inputs():
    from streak.params import ParameterError
    p = _tiny()
    with pytest.raises(ParameterError):
        simulate_arm(np.array([1.0, -1.0]), np.ones(3, bool), np.zeros((3, 2)), get_arm("A2"), p)
    with pytest.raises(ParameterError):
        simulate_arm(np.array([1.0, 1.0]), np.ones(4, bool), np.zeros((3, 2)), get_arm("A2"), p)
    with pytest.raises(ParameterError):
        simulate_arm(np.array([1.0, 1.0]), np.ones(3, bool), np.zeros((2, 2)), get_arm("A2"), p)
