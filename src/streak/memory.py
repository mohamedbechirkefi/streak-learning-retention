# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Memory model: forgetting curves and half-life update rules (protocol section 2).

Pure functions. Inputs are scalars or NumPy arrays; delays and half-lives in days.
"""

from __future__ import annotations

import numpy as np

from .params import FORMS, GAIN_RULES, ParameterError

#: Power-law constant chosen so that p = 0.5 at delay = h: 2**(1/0.5) - 1.
POWER_C = 3.0
POWER_EXPONENT = -0.5


def recall(delay, half_life, form: str = "exponential"):
    """Recall probability after ``delay`` days for an item with ``half_life`` days.

    exponential: p = 2 ** (-delay / h)
    power:       p = (1 + 3 delay / h) ** (-0.5)

    Both give p = 1 at delay 0 and p = 0.5 at delay = h. Raises ParameterError
    for negative delays, non-positive half-lives, non-finite inputs or an
    unknown form.
    """
    if form not in FORMS:
        raise ParameterError(f"unknown forgetting form {form!r}")
    d = np.asarray(delay, dtype=float)
    h = np.asarray(half_life, dtype=float)
    if not (np.all(np.isfinite(d)) and np.all(np.isfinite(h))):
        raise ParameterError("delay and half_life must be finite")
    if np.any(d < 0):
        raise ParameterError("delay must be non-negative")
    if np.any(h <= 0):
        raise ParameterError("half_life must be positive")
    if form == "exponential":
        p = np.exp2(-d / h)
    else:
        p = (1.0 + POWER_C * d / h) ** POWER_EXPONENT
    p = np.clip(p, 0.0, 1.0)
    return float(p) if p.ndim == 0 else p


def updated_half_life(h, p_at_review, success, *, gain_rule: str, g_min: float, a: float,
                      b: float, h_min: float):
    """Half-life after a review at which recall probability was ``p_at_review``.

    success, difficulty gain: h * (1 + g_min + a * (1 - p))
    success, flat gain:       h * (1 + g_min + a * 0.3)
    failure:                  max(h_min, b * h)
    """
    if gain_rule not in GAIN_RULES:
        raise ParameterError(f"unknown gain rule {gain_rule!r}")
    h = np.asarray(h, dtype=float)
    p = np.asarray(p_at_review, dtype=float)
    s = np.asarray(success, dtype=bool)
    if np.any(h <= 0) or not np.all(np.isfinite(h)):
        raise ParameterError("half_life must be finite and positive")
    if np.any((p < 0) | (p > 1)) or not np.all(np.isfinite(p)):
        raise ParameterError("p_at_review must lie in [0, 1]")
    if gain_rule == "difficulty":
        factor = 1.0 + g_min + a * (1.0 - p)
    else:
        factor = np.full_like(p, 1.0 + g_min + a * 0.3)
    out = np.where(s, h * factor, np.maximum(h_min, b * h))
    return float(out) if out.ndim == 0 else out
