# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Scheduling: planned slots, item selection and timing rules (protocol sections 3 and 8)."""

import numpy as np
import pytest

from streak.params import ModelParams, ParameterError, get_arm
from streak.population import generate_learners
from streak.simulate import planned_slots, select_items, simulate_arm


def test_planned_daily_default():
    plan = planned_slots("daily", ModelParams())
    assert plan[0] == 0 and np.all(plan[1:] == 12) and plan.sum() == 672


def test_planned_fixed_default():
    plan = planned_slots("fixed", ModelParams())
    days = np.nonzero(plan)[0]
    assert len(days) == 24 and np.all(plan[days] == 28) and plan.sum() == 672
    assert set(int(d) % 7 for d in days) == {1, 3, 5}


def test_planned_none():
    assert planned_slots("none", ModelParams()).sum() == 0


def test_planned_indivisible_budget_raises():
    with pytest.raises(ParameterError):
        planned_slots("daily", ModelParams(budget_slots=673))
    with pytest.raises(ParameterError):
        planned_slots("fixed", ModelParams(budget_slots=670))


def test_round_robin_wraps():
    p_hat = np.zeros(5)
    idx, ptr = select_items("round_robin", 3, p_hat, 3)
    assert list(idx) == [3, 4, 0] and ptr == 1


def test_easiest_and_most_due_with_ties():
    p_hat = np.array([0.2, 0.9, 0.5, 0.9, 0.1])
    assert list(select_items("easiest", 3, p_hat, 0)[0]) == [1, 3, 2]
    assert list(select_items("most_due", 2, p_hat, 0)[0]) == [4, 0]
    ties = np.full(4, 0.5)
    assert list(select_items("easiest", 2, ties, 0)[0]) == [0, 1]
    assert list(select_items("most_due", 2, ties, 0)[0]) == [0, 1]


def test_select_invalid():
    with pytest.raises(ParameterError):
        select_items("easiest", 6, np.zeros(5), 0)
    with pytest.raises(ParameterError):
        select_items("random", 1, np.zeros(5), 0)


def _run(arm, p, seed=9001, j=0):
    lr = generate_learners(seed, j + 1, p)[j]
    return simulate_arm(lr.initial_half_lives(p), lr.availability(p), lr.outcome_u, get_arm(arm), p)


def test_fixed_all_available_practises_exactly_on_scheduled_days():
    p = ModelParams(q=1.0)
    res = _run("A1", p)
    active = np.nonzero(res.daily_spent)[0]
    assert list(active) == [d for d in range(1, 57) if d % 7 in (1, 3, 5)]
    assert np.all(res.daily_spent[active] == 28)


@pytest.mark.parametrize("seed", [9001, 9002, 9003])
def test_fixed_only_on_scheduled_or_makeup_days(seed):
    p = ModelParams(q=0.6)
    res = _run("A1", p, seed)
    cum_plan = np.cumsum(res.planned)
    cum_spent = np.cumsum(res.daily_spent)
    for d in np.nonzero(res.daily_spent)[0]:
        owed = cum_plan[d] - cum_spent[d - 1]
        assert owed > 0, f"practice on day {d} without scheduled or carried slots"
        scheduled = d % 7 in (1, 3, 5)
        makeup = cum_plan[d - 1] - cum_spent[d - 1] > 0
        assert scheduled or makeup


@pytest.mark.parametrize("arm", ["A2", "A3", "D-RR"])
def test_daily_arms_practise_every_available_day(arm):
    p = ModelParams(q=0.7)
    res = _run(arm, p)
    assert np.array_equal(res.daily_spent[1:] > 0, res.available[1:])


def test_a2_a3_identical_timing():
    p = ModelParams(q=0.7)
    r2, r3 = _run("A2", p), _run("A3", p)
    assert np.array_equal(r2.daily_spent, r3.daily_spent)


def test_at_most_one_review_per_item_per_day():
    for arm in ["A1", "A2", "A3", "F-EASY"]:
        res = _run(arm, ModelParams(q=0.5))
        pairs = set(zip(res.review_day.tolist(), res.review_item.tolist()))
        assert len(pairs) == res.review_day.size


def test_day_one_ties_select_lowest_indices():
    # On day 1 every belief equals 2^(-1/h0): ties, so easiest and most-due both start at item 0.
    p = ModelParams(q=1.0)
    for arm in ["A2", "A3"]:
        res = _run(arm, p)
        assert list(res.review_item[res.review_day == 1]) == list(range(12))


def test_a2_reviews_highest_belief_items():
    """Replay A2's belief and check each day's choice is the top-n by estimated recall."""
    from streak.memory import recall, updated_half_life
    p = ModelParams(q=0.9)
    res = _run("A2", p, 9004)
    h_hat, s = np.full(p.n_items, p.h0), np.zeros(p.n_items)
    for d in range(1, p.horizon_days + 1):
        mask = res.review_day == d
        if not mask.any():
            continue
        items = res.review_item[mask]
        p_hat = recall(d - s, h_hat)
        chosen_min = p_hat[items].min()
        others = np.setdiff1d(np.arange(p.n_items), items)
        assert np.all(p_hat[others] <= chosen_min + 1e-15)
        h_hat[items] = updated_half_life(h_hat[items], p_hat[items], res.review_success[mask],
                                         gain_rule="difficulty", g_min=p.g_min, a=p.a, b=p.b, h_min=p.h_min)
        s[items] = d
