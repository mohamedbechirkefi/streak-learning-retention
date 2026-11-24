# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Per learner-arm metrics (protocol section 5). Pure functions of an ArmResult."""

from __future__ import annotations

import math

import numpy as np

from .memory import recall
from .params import ModelParams
from .simulate import ArmResult

#: Metric names in export order, with units. Retention metrics R{delay} are added per config.
ACTIVITY_METRICS = {
    "minutes_spent": "minutes",
    "slots_spent": "slots",
    "residual_slots": "slots",
    "reviews": "count",
    "active_days": "days",
    "longest_streak": "days",
    "final_streak": "days",
    "missed_unavailable_days": "days",
    "missed_available_days": "days",
    "practice_success_rate": "proportion",
    "item_coverage": "proportion",
}


def retention_at(res: ArmResult, delay: int, p: ModelParams) -> np.ndarray:
    """Per-item true recall probability at t = T + delay."""
    t = p.horizon_days + delay
    return recall(t - res.last_review, res.half_life, p.form)


def runs_of_true(x: np.ndarray) -> tuple[int, int]:
    """(longest run of True, run of True ending at the last element)."""
    longest = cur = 0
    for v in x:
        cur = cur + 1 if v else 0
        longest = max(longest, cur)
    return longest, cur


def learner_arm_metrics(res: ArmResult, p: ModelParams) -> dict[str, float | int | bool | None]:
    """All protocol metrics for one learner-arm, as plain Python numbers."""
    m: dict[str, float | int | bool | None] = {}
    for delay in p.retention_delays:
        m[f"R{delay}"] = float(np.mean(retention_at(res, delay, p)))
    auc_grid = [float(np.mean(retention_at(res, d, p))) for d in range(p.auc_max_delay + 1)]
    m["AUC_R"] = float(np.mean(auc_grid))
    r30_items = np.sort(retention_at(res, 30, p))
    n_dec = max(1, int(round(0.1 * p.n_items)))
    m["weakest_decile_R30"] = float(np.mean(r30_items[:n_dec]))

    days = slice(1, p.horizon_days + 1)
    active = res.daily_spent[days] > 0
    avail = res.available[days]
    slots = int(res.daily_spent.sum())
    longest, final = runs_of_true(active)
    n_rev = int(res.review_day.size)
    m["minutes_spent"] = slots * p.slot_minutes
    m["slots_spent"] = slots
    m["residual_slots"] = int(res.residual)
    m["reviews"] = n_rev
    m["active_days"] = int(active.sum())
    m["longest_streak"] = int(longest)
    m["final_streak"] = int(final)
    m["missed_unavailable_days"] = int((~avail).sum())
    m["missed_available_days"] = int((avail & ~active).sum())
    m["practice_success_rate"] = float(res.review_success.mean()) if n_rev else None
    m["item_coverage"] = float(np.unique(res.review_item).size / p.n_items)
    m["residual_flag"] = bool(res.residual > p.residual_flag_fraction * p.budget_slots)
    for k, v in m.items():
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError(f"metric {k} is not finite")
    return m
