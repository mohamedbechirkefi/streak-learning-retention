# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Model parameters and arm definitions (research/protocol.md sections 2, 3, 10).

Units: time in days; budget in slots (one slot = ``slot_minutes`` minutes);
half-lives in days; probabilities are unitless proportions in [0, 1].
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, fields, replace
from typing import Any

FORMS = ("exponential", "power")
GAIN_RULES = ("difficulty", "flat")
TIMINGS = ("none", "daily", "fixed")
SELECTIONS = ("none", "round_robin", "easiest", "most_due", "due_threshold")


class ParameterError(ValueError):
    """Raised for an invalid parameter value (explicit error path)."""


_FLOAT_FIELDS = ("slot_minutes", "h0", "sigma_item", "sigma_learner", "g_min", "a", "b", "h_min", "q",
                 "residual_flag_fraction")


@dataclass(frozen=True)
class ModelParams:
    """Parameters of the synthetic learner model. Defaults are protocol v0.1-draft
    planning values (research/protocol.md section 10), not measurements."""

    n_items: int = 100  # K, items per learner
    horizon_days: int = 56  # T, practice days 1..T
    budget_slots: int = 672  # M, slots per learner over the horizon
    slot_minutes: float = 0.5  # minutes per slot (one review)
    daily_cap_slots: int = 60  # maximum slots spent on one day
    fixed_weekdays: tuple[int, ...] = (1, 3, 5)  # A1 sessions on days d with d mod 7 in this set
    h0: float = 1.0  # median initial half-life, days
    sigma_item: float = 0.5  # log-sd of item difficulty u_i
    sigma_learner: float = 0.3  # log-sd of learner ability theta_l
    g_min: float = 0.1  # minimum relative gain on success
    a: float = 2.5  # difficulty-dependent gain coefficient
    b: float = 0.6  # half-life multiplier on failure
    h_min: float = 0.25  # half-life floor after failure, days
    q: float = 0.85  # daily availability probability
    form: str = "exponential"  # true forgetting form
    gain_rule: str = "difficulty"  # true update rule on success
    retention_delays: tuple[int, ...] = (1, 7, 30, 90)  # days after T
    auc_max_delay: int = 90  # AUC-R is the mean of R over delays 0..auc_max_delay
    residual_flag_fraction: float = 0.05  # residual > fraction * M is flagged

    def __post_init__(self) -> None:
        # JSON configs may carry real-valued parameters as integers (for example "h0": 1).
        # Coerce them to float so no array derived from them is silently integer-typed
        # (bug found by the exploratory EXP-002 smoke run, decision D-008).
        for name in _FLOAT_FIELDS:
            v = getattr(self, name)
            if isinstance(v, int) and not isinstance(v, bool):
                object.__setattr__(self, name, float(v))
        validate_params(self)

    @property
    def g_flat(self) -> float:
        """Flat gain, equal to the difficulty-dependent gain at p = 0.7."""
        return self.g_min + self.a * 0.3

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["fixed_weekdays"] = list(self.fixed_weekdays)
        d["retention_delays"] = list(self.retention_delays)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ModelParams":
        known = {f.name for f in fields(cls)}
        unknown = set(d) - known
        if unknown:
            raise ParameterError(f"unknown model parameter(s): {sorted(unknown)}")
        kw = dict(d)
        for key in ("fixed_weekdays", "retention_delays"):
            if key in kw:
                kw[key] = tuple(kw[key])
        return cls(**kw)

    def with_updates(self, **kw: Any) -> "ModelParams":
        return replace(self, **kw)


def _finite_positive(name: str, v: float) -> None:
    if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) or v <= 0:
        raise ParameterError(f"{name} must be a finite positive number, got {v!r}")


def _positive_int(name: str, v: int, allow_zero: bool = False) -> None:
    if not isinstance(v, int) or isinstance(v, bool) or v < 0 or (v == 0 and not allow_zero):
        raise ParameterError(f"{name} must be a {'non-negative' if allow_zero else 'positive'} integer, got {v!r}")


def validate_params(p: ModelParams) -> None:
    _positive_int("n_items", p.n_items)
    _positive_int("horizon_days", p.horizon_days)
    _positive_int("budget_slots", p.budget_slots, allow_zero=True)
    _positive_int("daily_cap_slots", p.daily_cap_slots)
    _positive_int("auc_max_delay", p.auc_max_delay, allow_zero=True)
    for name in ("slot_minutes", "h0", "h_min", "a"):
        _finite_positive(name, getattr(p, name))
    for name in ("sigma_item", "sigma_learner", "g_min"):
        v = getattr(p, name)
        if not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
            raise ParameterError(f"{name} must be a finite non-negative number, got {v!r}")
    if not (0 < p.b < 1):
        raise ParameterError(f"b must lie in (0, 1), got {p.b!r}")
    if not (0 <= p.q <= 1):
        raise ParameterError(f"q must lie in [0, 1], got {p.q!r}")
    if not (0 <= p.residual_flag_fraction <= 1):
        raise ParameterError("residual_flag_fraction must lie in [0, 1]")
    if p.form not in FORMS:
        raise ParameterError(f"form must be one of {FORMS}, got {p.form!r}")
    if p.gain_rule not in GAIN_RULES:
        raise ParameterError(f"gain_rule must be one of {GAIN_RULES}, got {p.gain_rule!r}")
    if not p.fixed_weekdays or any((not isinstance(w, int)) or w < 0 or w > 6 for w in p.fixed_weekdays):
        raise ParameterError("fixed_weekdays must be a non-empty set of integers in 0..6")
    if len(set(p.fixed_weekdays)) != len(p.fixed_weekdays):
        raise ParameterError("fixed_weekdays must not repeat")
    if not p.retention_delays or any((not isinstance(x, int)) or x < 0 for x in p.retention_delays):
        raise ParameterError("retention_delays must be non-negative integers")
    if 30 not in p.retention_delays:
        raise ParameterError("retention_delays must include 30 (primary metric R30)")


@dataclass(frozen=True)
class ArmSpec:
    """A scheduling arm: when to practise (timing) and which items (selection)."""

    name: str
    timing: str
    selection: str
    role: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if self.timing not in TIMINGS:
            raise ParameterError(f"timing must be one of {TIMINGS}, got {self.timing!r}")
        if self.selection not in SELECTIONS:
            raise ParameterError(f"selection must be one of {SELECTIONS}, got {self.selection!r}")
        if (self.timing == "none") != (self.selection == "none"):
            raise ParameterError("timing 'none' and selection 'none' go together (no-practice control)")


#: Arms of EXP-001 (protocol section 3) and the extra policy cells of EXP-003.
ARMS: dict[str, ArmSpec] = {
    "A0": ArmSpec("A0", "none", "none", "negative control: no practice after day 0"),
    "A1": ArmSpec("A1", "fixed", "round_robin", "primary baseline: 3 fixed weekdays, round-robin"),
    "A2": ArmSpec("A2", "daily", "easiest", "treatment: streak-driven, easiest first"),
    "A3": ArmSpec("A3", "daily", "due_threshold", "comparator: threshold-based spaced repetition (r* = 0.9)"),
    "D-RR": ArmSpec("D-RR", "daily", "round_robin", "EXP-003 cell: daily, round-robin"),
    "F-EASY": ArmSpec("F-EASY", "fixed", "easiest", "EXP-003 cell: 3 per week, easiest first"),
    "F-DUE": ArmSpec("F-DUE", "fixed", "due_threshold", "EXP-003 cell: 3 per week, threshold-based spaced repetition"),
}


def get_arm(name: str) -> ArmSpec:
    try:
        return ARMS[name]
    except KeyError:
        raise ParameterError(f"unknown arm {name!r}; known arms: {sorted(ARMS)}") from None
