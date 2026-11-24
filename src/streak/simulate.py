# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Simulation of one synthetic learner under one scheduling arm (protocol sections 2, 3).

``simulate_arm`` is a pure function of its inputs: initial half-lives, an
availability vector, a matrix of outcome uniforms, an arm and the model
parameters. It returns the final memory state and a trace of every review.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .memory import recall, updated_half_life
from .params import ArmSpec, ModelParams, ParameterError

BELIEF_FORM = "exponential"
BELIEF_GAIN = "difficulty"


def planned_slots(timing: str, p: ModelParams) -> np.ndarray:
    """Slots planned for each day 0..T (index 0 is the initial-study day, always 0).

    daily: M / T slots on every day 1..T (M must be divisible by T).
    fixed: M / n slots on each of the n days with d mod 7 in ``fixed_weekdays``.
    none: no slots.
    """
    plan = np.zeros(p.horizon_days + 1, dtype=np.int64)
    if timing == "none":
        return plan
    if timing == "daily":
        days = np.arange(1, p.horizon_days + 1)
    elif timing == "fixed":
        days = np.array([d for d in range(1, p.horizon_days + 1) if d % 7 in p.fixed_weekdays])
    else:
        raise ParameterError(f"unknown timing {timing!r}")
    if days.size == 0:
        raise ParameterError("timing has no scheduled day within the horizon")
    if p.budget_slots % days.size:
        raise ParameterError(
            f"budget_slots={p.budget_slots} is not divisible by the {days.size} scheduled days "
            f"of timing {timing!r}; the matched-minutes design needs an integer per-session budget"
        )
    plan[days] = p.budget_slots // days.size
    return plan


def select_items(selection: str, n: int, p_hat: np.ndarray, rr_pointer: int) -> tuple[np.ndarray, int]:
    """Choose ``n`` distinct items. Returns (indices, new round-robin pointer).

    round_robin: the next n items in fixed order 0..K-1, cyclically.
    easiest: highest estimated recall first (ties: lower index first).
    most_due: lowest estimated recall first (ties: lower index first).
    """
    k = p_hat.shape[0]
    if not 0 <= n <= k:
        raise ParameterError(f"cannot select {n} distinct items out of {k}")
    if selection == "round_robin":
        idx = (rr_pointer + np.arange(n)) % k
        return idx, int((rr_pointer + n) % k)
    if selection == "easiest":
        return np.argsort(-p_hat, kind="stable")[:n], rr_pointer
    if selection == "most_due":
        return np.argsort(p_hat, kind="stable")[:n], rr_pointer
    raise ParameterError(f"unknown selection {selection!r}")


@dataclass
class ArmResult:
    """Final state and trace of one learner-arm simulation."""

    half_life: np.ndarray  # true half-lives at the end of day T, days
    last_review: np.ndarray  # time of last exposure per item, days
    daily_spent: np.ndarray  # slots spent per day 0..T
    planned: np.ndarray  # slots planned per day 0..T
    residual: int  # unspent slots at the end of day T
    available: np.ndarray  # availability per day 0..T
    review_day: np.ndarray  # one entry per review event
    review_item: np.ndarray
    review_success: np.ndarray
    review_p_true: np.ndarray


def simulate_arm(h_init: np.ndarray, available: np.ndarray, outcome_u: np.ndarray,
                 arm: ArmSpec, p: ModelParams) -> ArmResult:
    """Simulate one learner under one arm over days 1..T.

    Carry-forward: planned slots accumulate in ``pending`` and are spent on the
    next available day, up to min(daily cap, K) slots (at most one review per item
    per day). Whatever is still pending after day T is the residual, so
    sum(daily_spent) + residual == M for every practising arm.
    """
    k, t_end = p.n_items, p.horizon_days
    h = np.array(h_init, dtype=float)
    if h.shape != (k,) or np.any(~np.isfinite(h)) or np.any(h <= 0):
        raise ParameterError("h_init must be K finite positive half-lives")
    av = np.asarray(available, dtype=bool)
    if av.shape != (t_end + 1,):
        raise ParameterError("available must have length T + 1")
    u = np.asarray(outcome_u, dtype=float)
    if u.shape != (t_end + 1, k):
        raise ParameterError("outcome_u must have shape (T + 1, K)")

    s = np.zeros(k)  # initial study at t = 0
    h_hat = np.full(k, float(p.h0), dtype=float)  # scheduler belief: population-median learner and item
    plan = planned_slots(arm.timing, p)
    spent = np.zeros(t_end + 1, dtype=np.int64)
    pending = 0
    rr = 0
    max_per_day = min(p.daily_cap_slots, k)
    log_d, log_i, log_s, log_p = [], [], [], []
    for d in range(1, t_end + 1):
        pending += int(plan[d])
        if not av[d] or pending == 0:
            continue
        n = min(pending, max_per_day)
        p_hat = recall(d - s, h_hat, BELIEF_FORM)
        idx, rr = select_items(arm.selection, n, p_hat, rr)
        p_true = recall(d - s[idx], h[idx], p.form)
        success = u[d, idx] < p_true
        h[idx] = updated_half_life(h[idx], p_true, success, gain_rule=p.gain_rule,
                                   g_min=p.g_min, a=p.a, b=p.b, h_min=p.h_min)
        h_hat[idx] = updated_half_life(h_hat[idx], p_hat[idx], success, gain_rule=BELIEF_GAIN,
                                       g_min=p.g_min, a=p.a, b=p.b, h_min=p.h_min)
        s[idx] = d
        spent[d] = n
        pending -= n
        log_d.append(np.full(n, d))
        log_i.append(idx)
        log_s.append(success)
        log_p.append(p_true)

    def cat(parts, dtype):
        return np.concatenate(parts).astype(dtype) if parts else np.zeros(0, dtype=dtype)

    return ArmResult(h, s, spent, plan, int(pending), av,
                     cat(log_d, np.int64), cat(log_i, np.int64), cat(log_s, bool), cat(log_p, float))
