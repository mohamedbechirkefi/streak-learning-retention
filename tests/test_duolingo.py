# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Ingestion and calibration on the Duolingo trace schema (protocol section 14),
tested on an invented fixture only (never real rows)."""

import csv
import gzip
import math
from pathlib import Path

import numpy as np
import pytest

from streak import duolingo as dl

FIXTURE = Path(__file__).parent / "fixtures" / "duolingo_synthetic.csv"
SIGMA = math.sqrt(0.5 ** 2 + 0.3 ** 2)


def _rows():
    with open(FIXTURE, newline="") as f:
        r = csv.DictReader(f)
        dl.check_header(r.fieldnames)
        return list(r)


def test_fixture_counts_and_exclusion_order():
    proc = dl.ingest(_rows())
    c = proc.counts()
    assert c["rows_read"] == 12
    assert c["exclusions"] == {"schema_invalid": 4, "not_first_repeat": 1, "delta_below_1_day": 1,
                               "delta_above_90_days": 1}
    assert c["kept"] == 5
    assert c["rows_read"] == c["kept"] + sum(c["exclusions"].values())
    assert c["missing_by_column"]["delta"] == 1 and c["missing_by_column"]["user_id"] == 1
    assert sum(c["missing_by_column"].values()) == 2
    assert c["invalid_detail"] == {"p_recall != session_correct / session_seen": 1, "parse error: ValueError": 1,
                                   "user_id missing": 1, "history counts inconsistent": 1}
    assert proc.delta_days.tolist() == [2.0, 5.0, 20.0, 7.0, 1.0]
    assert proc.n.tolist() == [2, 2, 1, 4, 1] and proc.k.tolist() == [2, 1, 0, 3, 1]
    assert c["kept_fit"] + c["kept_heldout"] == 5


def test_ingest_is_pure_and_deterministic():
    rows = _rows()
    a, b = dl.ingest(rows), dl.ingest(rows)
    assert a.split.tolist() == b.split.tolist() and a.delta_days.tolist() == b.delta_days.tolist()
    assert rows == _rows()  # input not mutated


def test_split_is_by_user_hash():
    import hashlib
    for uid in ["synthU01", "synthU02", "synthU03", "x"]:
        even = hashlib.sha256(uid.encode()).digest()[0] % 2 == 0
        assert dl.split_of(uid) == ("fit" if even else "heldout")
    # Same user, same split, for all their rows.
    proc = dl.ingest(_rows())
    users = [r["user_id"] for r in _rows()][:5]  # the five kept rows are the first five
    assert proc.split.tolist() == [0 if dl.split_of(u) == "fit" else 1 for u in users]


def test_header_check_and_gzip_reader(tmp_path):
    with pytest.raises(dl.IngestError):
        dl.check_header(["p_recall", "delta"])
    gz = tmp_path / "f.csv.gz"
    with gzip.open(gz, "wt", newline="") as f:
        f.write(FIXTURE.read_text())
    assert len(list(dl.read_rows(gz))) == 12
    bad = tmp_path / "bad.csv.gz"
    with gzip.open(bad, "wt") as f:
        f.write("a,b\n1,2\n")
    with pytest.raises(dl.IngestError):
        list(dl.read_rows(bad))


def test_processed_roundtrip(tmp_path):
    proc = dl.ingest(_rows())
    dl.save_processed(proc, tmp_path / "p.npz")
    back = dl.load_processed(tmp_path / "p.npz")
    assert back.delta_days.tolist() == proc.delta_days.tolist() and back.k.tolist() == proc.k.tolist()


def test_marginal_recall_limits():
    # sigma = 0 reduces to the exponential curve; p = 0.5 at delta = h0.
    assert dl.marginal_recall(np.array([3.0]), 3.0, 0.0)[0] == pytest.approx(0.5)
    assert dl.marginal_recall(np.array([3.0]), 3.0, 0.0, "power")[0] == pytest.approx(0.5)
    p = dl.marginal_recall(np.array([1.0, 5.0, 30.0]), 4.0, SIGMA)
    assert np.all(np.diff(p) < 0) and np.all((p > 0) & (p < 1))
    with pytest.raises(ValueError):
        dl.marginal_recall(np.array([1.0]), 1.0, 0.1, "linear")


def _synthetic(h0, n_rows, seed, form="exponential"):
    rng = np.random.default_rng(seed)
    delta = rng.uniform(1, 90, n_rows)
    h = h0 * np.exp(SIGMA * rng.standard_normal(n_rows))
    p = np.exp2(-delta / h) if form == "exponential" else (1 + 3 * delta / h) ** -0.5
    n = rng.integers(1, 5, n_rows)
    k = rng.binomial(n, p)
    return delta, n, k


def test_fit_recovers_h0_on_simulated_data():
    delta, n, k = _synthetic(6.0, 20000, 1)
    fit = dl.fit_h0(delta, n, k, SIGMA)
    assert fit["h0_days"] == pytest.approx(6.0, rel=0.05)
    lo, hi = fit["lr95_naive_days"]
    assert lo < fit["h0_days"] < hi
    assert not fit["on_grid_edge"]
    assert fit["n_rows"] == 20000 and fit["n_trials"] == int(n.sum())
    # Deterministic.
    assert dl.fit_h0(delta, n, k, SIGMA)["h0_days"] == fit["h0_days"]


def test_fit_flags_grid_edge_and_empty_input():
    delta = np.array([1.0, 2.0])
    fit = dl.fit_h0(delta, np.array([5, 5]), np.array([5, 5]), SIGMA)  # perfect recall: h0 -> upper edge
    assert fit["on_grid_edge"]
    with pytest.raises(ValueError):
        dl.fit_h0(np.array([]), np.array([], int), np.array([], int), SIGMA)


def test_heldout_evaluation_prefers_true_form():
    d1, n1, k1 = _synthetic(8.0, 8000, 2)
    d2, n2, k2 = _synthetic(8.0, 8000, 3)
    train = dl.Processed(np.zeros(d1.size, np.int8), d1, n1, k1)
    test = dl.Processed(np.ones(d2.size, np.int8), d2, n2, k2)
    ev = dl.heldout_evaluation(train, test, SIGMA)
    assert ev["exponential"]["ll_per_trial"] > ev["constant"]["ll_per_trial"]
    assert ev["exponential"]["ll_per_trial"] > ev["power"]["ll_per_trial"]
    cal = ev["exponential"]["calibration"]
    assert len(cal) == 6 and sum(b["trials"] for b in cal) == int(n2.sum())
    assert all(abs(b["observed"] - b["predicted"]) < 0.05 for b in cal if b["trials"] > 500)
