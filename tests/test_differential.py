# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Differential test: the vectorised engine against an independent, naive pure-Python
reference written directly from research/protocol.md section 2 (no NumPy, no shared code)."""

import math

import pytest

from streak.metrics import learner_arm_metrics
from streak.params import ModelParams, get_arm
from streak.population import generate_learners
from streak.simulate import simulate_arm


def ref_recall(delay, h, form):
    return 2.0 ** (-delay / h) if form == "exponential" else (1 + 3 * delay / h) ** -0.5


def ref_new_h(h, p, ok, rule, P):
    if not ok:
        return max(P.h_min, P.b * h)
    return h * (1 + P.g_min + (P.a * (1 - p) if rule == "difficulty" else P.a * 0.3))


def reference(h_init, avail, U, timing, selection, P):
    K, T = P.n_items, P.horizon_days
    h, hh, s = list(h_init), [P.h0] * K, [0.0] * K
    if timing == "daily":
        sched = {d: P.budget_slots // T for d in range(1, T + 1)}
    elif timing == "fixed":
        days = [d for d in range(1, T + 1) if d % 7 in P.fixed_weekdays]
        sched = {d: P.budget_slots // len(days) for d in days}
    else:
        sched = {}
    owed, ptr, spent, log = 0, 0, [0] * (T + 1), []
    for d in range(1, T + 1):
        owed += sched.get(d, 0)
        if not avail[d] or owed == 0:
            continue
        n = min(owed, P.daily_cap_slots, K)
        est = [ref_recall(d - s[i], hh[i], "exponential") for i in range(K)]
        if selection == "round_robin":
            items = [(ptr + j) % K for j in range(n)]
            ptr = (ptr + n) % K
        elif selection == "easiest":
            items = sorted(range(K), key=lambda i: (-est[i], i))[:n]
        else:
            items = sorted(range(K), key=lambda i: (est[i], i))[:n]
        for i in items:
            pt = ref_recall(d - s[i], h[i], P.form)
            ok = U[d][i] < pt
            h[i] = ref_new_h(h[i], pt, ok, P.gain_rule, P)
            hh[i] = ref_new_h(hh[i], est[i], ok, "difficulty", P)
            s[i] = d
            log.append((d, i, ok))
        spent[d] = n
        owed -= n
    r30 = sum(ref_recall(T + 30 - s[i], h[i], P.form) for i in range(K)) / K
    return h, s, spent, owed, log, r30


CASES = [(arm, form, gain, q) for arm in ["A0", "A1", "A2", "A3", "D-RR", "F-EASY", "F-DUE"]
         for form, gain in [("exponential", "difficulty"), ("power", "flat")] for q in (0.6, 1.0)]


@pytest.mark.parametrize("arm,form,gain,q", CASES)
def test_engine_matches_reference(arm, form, gain, q):
    P = ModelParams(n_items=12, horizon_days=21, budget_slots=63, daily_cap_slots=7, q=q,
                    form=form, gain_rule=gain, h0=1.5)
    for lr in generate_learners(9101, 4, P):
        h_init = lr.initial_half_lives(P)
        avail = lr.availability(P)
        res = simulate_arm(h_init, avail, lr.outcome_u, get_arm(arm), P)
        spec = get_arm(arm)
        h, s, spent, owed, log, r30 = reference(h_init.tolist(), avail.tolist(), lr.outcome_u.tolist(),
                                                spec.timing, spec.selection, P)
        assert res.half_life.tolist() == pytest.approx(h, rel=1e-12)
        assert res.last_review.tolist() == s
        assert res.daily_spent.tolist() == spent
        assert res.residual == owed
        assert sorted(zip(res.review_day.tolist(), res.review_item.tolist(), res.review_success.tolist())) == sorted(log)
        assert learner_arm_metrics(res, P)["R30"] == pytest.approx(r30, rel=1e-12)
        assert math.isfinite(r30)
