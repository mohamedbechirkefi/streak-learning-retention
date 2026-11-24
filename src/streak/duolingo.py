# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Ingestion and calibration on the Duolingo half-life regression traces
(Settles and Meeder 2016; Harvard Dataverse doi:10.7910/DVN/N8XJME, CC BY-NC 4.0).

Role in the study (research/protocol.md, "Amendments before freeze, round 2"):
the real traces set one parameter of the synthetic model, the median initial
half-life h0, by a method fixed in the protocol before fitting, on a user split
that never touches the simulation's primary contrast. A held-out user split is
kept for a preregistered second test of the forgetting model (evaluated after
the freeze, never used to fit).

Everything here is a pure function of its inputs except ``read_rows`` (file I/O).
No user id is stored in the processed form; it is used only to assign the split.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np

RAW_COLUMNS = ("p_recall", "timestamp", "delta", "user_id", "learning_language", "ui_language",
               "lexeme_id", "lexeme_string", "history_seen", "history_correct", "session_seen",
               "session_correct")

SECONDS_PER_DAY = 86400.0
#: Protocol round-2 amendment: first-repeat observations with delta in [1, 90] days.
MIN_DELTA_DAYS = 1.0
MAX_DELTA_DAYS = 90.0
#: p_recall must equal session_correct / session_seen within this tolerance.
P_RECALL_TOL = 1e-3
#: Calibration-curve bins for the second test, in days (last bin closed at 90).
CALIBRATION_BINS = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 90.0)

EXCLUSION_REASONS = ("schema_invalid", "not_first_repeat", "delta_below_1_day", "delta_above_90_days")


class IngestError(ValueError):
    """Raised when the raw file does not have the expected schema."""


def split_of(user_id: str) -> str:
    """Deterministic user split: 'fit' if the first byte of SHA-256(user_id) is even, else 'heldout'."""
    return "fit" if hashlib.sha256(user_id.encode("utf-8")).digest()[0] % 2 == 0 else "heldout"


def read_rows(path: Path) -> Iterator[dict]:
    """Stream rows of the raw gzipped CSV as dictionaries of strings (file I/O, not pure)."""
    with gzip.open(path, "rt", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        check_header(reader.fieldnames)
        yield from reader


def check_header(fieldnames: Iterable[str] | None) -> None:
    got = tuple(fieldnames or ())
    if got != RAW_COLUMNS:
        raise IngestError(f"unexpected columns {got}; expected {RAW_COLUMNS}")


def _int(s: str) -> int:
    v = int(s)
    return v


def validate_row(row: dict) -> tuple[bool, str]:
    """(valid, reason). Types and ranges of the columns the study uses."""
    try:
        if not row.get("user_id"):
            return False, "user_id missing"
        p = float(row["p_recall"])
        delta = _int(row["delta"])
        hs, hc = _int(row["history_seen"]), _int(row["history_correct"])
        ss, sc = _int(row["session_seen"]), _int(row["session_correct"])
        _int(row["timestamp"])
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"parse error: {type(exc).__name__}"
    if not (0.0 <= p <= 1.0):
        return False, "p_recall outside [0, 1]"
    if delta < 0:
        return False, "negative delta"
    if hs < 0 or hc < 0 or hc > hs:
        return False, "history counts inconsistent"
    if ss < 1 or sc < 0 or sc > ss:
        return False, "session counts inconsistent"
    if abs(p - sc / ss) > P_RECALL_TOL:
        return False, "p_recall != session_correct / session_seen"
    return True, ""


@dataclass
class Processed:
    """Processed first-repeat observations (no identifiers) and the ingestion counts."""

    split: np.ndarray  # 0 = fit, 1 = heldout
    delta_days: np.ndarray
    n: np.ndarray  # session_seen (trials)
    k: np.ndarray  # session_correct (successes)
    n_rows_read: int = 0
    missing: dict = field(default_factory=dict)  # empty-string count per column
    exclusions: dict = field(default_factory=dict)  # count per reason, applied in EXCLUSION_REASONS order
    invalid_detail: dict = field(default_factory=dict)

    def counts(self) -> dict:
        kept = int(self.split.size)
        return {
            "rows_read": self.n_rows_read,
            "missing_by_column": dict(self.missing),
            "exclusions": dict(self.exclusions),
            "invalid_detail": dict(self.invalid_detail),
            "kept": kept,
            "kept_fit": int(np.sum(self.split == 0)),
            "kept_heldout": int(np.sum(self.split == 1)),
            "trials_fit": int(self.n[self.split == 0].sum()),
            "trials_heldout": int(self.n[self.split == 1].sum()),
        }


def ingest(rows: Iterable[dict]) -> Processed:
    """Pure: raw rows -> first-repeat observations with split, delta (days), trials, successes.

    Exclusions, in order: schema_invalid; not_first_repeat (history_seen != 1);
    delta_below_1_day; delta_above_90_days. Every row read is counted exactly once,
    either as kept or under one exclusion reason.
    """
    missing = {c: 0 for c in RAW_COLUMNS}
    excl = {r: 0 for r in EXCLUSION_REASONS}
    detail: dict[str, int] = {}
    sp: list[int] = []
    dd: list[float] = []
    nn: list[int] = []
    kk: list[int] = []
    n_read = 0
    for row in rows:
        n_read += 1
        for c in RAW_COLUMNS:
            if row.get(c, "") in ("", None):
                missing[c] += 1
        ok, why = validate_row(row)
        if not ok:
            excl["schema_invalid"] += 1
            detail[why] = detail.get(why, 0) + 1
            continue
        if int(row["history_seen"]) != 1:
            excl["not_first_repeat"] += 1
            continue
        days = int(row["delta"]) / SECONDS_PER_DAY
        if days < MIN_DELTA_DAYS:
            excl["delta_below_1_day"] += 1
            continue
        if days > MAX_DELTA_DAYS:
            excl["delta_above_90_days"] += 1
            continue
        sp.append(0 if split_of(row["user_id"]) == "fit" else 1)
        dd.append(days)
        nn.append(int(row["session_seen"]))
        kk.append(int(row["session_correct"]))
    return Processed(np.array(sp, dtype=np.int8), np.array(dd, dtype=float), np.array(nn, dtype=np.int64),
                     np.array(kk, dtype=np.int64), n_read, missing, excl, detail)


def save_processed(proc: Processed, path: Path) -> None:
    np.savez_compressed(path, split=proc.split, delta_days=proc.delta_days, n=proc.n, k=proc.k)


def load_processed(path: Path) -> Processed:
    z = np.load(path)
    return Processed(z["split"], z["delta_days"], z["n"], z["k"])


# ---------------------------------------------------------------------------
# Calibration of h0 (method fixed in the protocol before fitting)
# ---------------------------------------------------------------------------

_GH_NODES, _GH_WEIGHTS = np.polynomial.hermite_e.hermegauss(40)
_GH_WEIGHTS = _GH_WEIGHTS / _GH_WEIGHTS.sum()  # expectation over a standard normal


def _recall(delta: np.ndarray, h: np.ndarray, form: str) -> np.ndarray:
    if form == "exponential":
        return np.exp2(-delta / h)
    if form == "power":
        return (1.0 + 3.0 * delta / h) ** -0.5
    raise ValueError(f"unknown form {form!r}")


def marginal_recall(delta_days: np.ndarray, h0: float, sigma: float, form: str = "exponential") -> np.ndarray:
    """E[p(delta)] with log h ~ Normal(log h0, sigma^2) (40-node Gauss-Hermite)."""
    d = np.asarray(delta_days, dtype=float)[:, None]
    h = h0 * np.exp(sigma * _GH_NODES)[None, :]
    return _recall(d, h, form) @ _GH_WEIGHTS


def log_likelihood(h0: float, delta_days: np.ndarray, n: np.ndarray, k: np.ndarray, sigma: float,
                   form: str = "exponential") -> float:
    """Binomial log-likelihood (without the constant binomial coefficient)."""
    p = np.clip(marginal_recall(delta_days, h0, sigma, form), 1e-12, 1 - 1e-12)
    return float(np.sum(k * np.log(p) + (n - k) * np.log1p(-p)))


def fit_h0(delta_days: np.ndarray, n: np.ndarray, k: np.ndarray, sigma: float, form: str = "exponential",
           log_lo: float = math.log(0.05), log_hi: float = math.log(1000.0)) -> dict:
    """Maximum-likelihood h0 (days): grid over log h0 (121 points), then golden-section
    refinement in the bracket around the best grid point (tolerance 1e-6 in log h0).
    Deterministic. Also returns a likelihood-ratio 95% interval (chi-square 1 df,
    which treats trials as independent and is therefore optimistic)."""
    if delta_days.size == 0:
        raise ValueError("no observations to fit")
    f = lambda lh: log_likelihood(math.exp(lh), delta_days, n, k, sigma, form)  # noqa: E731
    grid = np.linspace(log_lo, log_hi, 121)
    vals = np.array([f(g) for g in grid])
    i = int(np.argmax(vals))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, grid.size - 1)]
    gr = (math.sqrt(5) - 1) / 2
    c, d = hi - gr * (hi - lo), lo + gr * (hi - lo)
    fc, fd = f(c), f(d)
    while hi - lo > 1e-6:
        if fc > fd:
            hi, d, fd = d, c, fc
            c = hi - gr * (hi - lo)
            fc = f(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + gr * (hi - lo)
            fd = f(d)
    best = (lo + hi) / 2
    ll = f(best)
    cut = ll - 1.920729  # chi2(1) 0.95 / 2

    def edge(direction: int) -> float | None:
        step, x = 0.001, best
        while log_lo <= x <= log_hi:
            x += direction * step
            if f(x) < cut:
                return math.exp(x)
            step *= 1.5
        return None

    return {"form": form, "sigma": sigma, "h0_days": math.exp(best), "log_likelihood": ll,
            "lr95_naive_days": [edge(-1), edge(+1)], "on_grid_edge": i in (0, grid.size - 1),
            "n_rows": int(delta_days.size), "n_trials": int(n.sum()), "n_successes": int(k.sum())}


def heldout_evaluation(train: Processed, test: Processed, sigma: float) -> dict:
    """Preregistered second test (evaluated once, after the freeze): fit h0 on ``train`` for
    the exponential and the power-law form; on ``test`` report the mean log-likelihood per
    trial of each and of a constant-recall baseline (pooled train recall), and a calibration
    table (observed versus predicted recall) by delta bins."""
    out: dict = {"sigma": sigma, "n_test_rows": int(test.delta_days.size), "n_test_trials": int(test.n.sum())}
    p_const = float(train.k.sum() / train.n.sum())
    tn, tk = test.n, test.k
    pc = min(max(p_const, 1e-12), 1 - 1e-12)
    out["constant"] = {"p": p_const,
                       "ll_per_trial": float((tk * math.log(pc) + (tn - tk) * math.log1p(-pc)).sum() / tn.sum())}
    bins = np.array(CALIBRATION_BINS)
    which = np.clip(np.searchsorted(bins, test.delta_days, side="right") - 1, 0, bins.size - 2)
    for form in ("exponential", "power"):
        fit = fit_h0(train.delta_days, train.n, train.k, sigma, form)
        p = marginal_recall(test.delta_days, fit["h0_days"], sigma, form)
        ll = log_likelihood(fit["h0_days"], test.delta_days, tn, tk, sigma, form)
        cal = []
        for b in range(bins.size - 1):
            m = which == b
            if not m.any():
                cal.append({"bin": [float(bins[b]), float(bins[b + 1])], "trials": 0})
                continue
            cal.append({"bin": [float(bins[b]), float(bins[b + 1])], "trials": int(tn[m].sum()),
                        "observed": float(tk[m].sum() / tn[m].sum()),
                        "predicted": float((p[m] * tn[m]).sum() / tn[m].sum())})
        out[form] = {"h0_days_train": fit["h0_days"], "ll_per_trial": ll / float(tn.sum()), "calibration": cal}
    return out


def subset(proc: Processed, split: int) -> Processed:
    m = proc.split == split
    return Processed(proc.split[m], proc.delta_days[m], proc.n[m], proc.k[m])
