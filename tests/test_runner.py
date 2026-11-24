# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Runner: config to results, determinism, failure recording and the G-FREEZE gate."""

import copy
import hashlib
import json
import shutil

import pytest

import streak.runner as runner
from streak.runner import (GateError, check_config, dump_result, execute, expand_cells,
                           protocol_freeze_status, run_experiment)
from streak.schema import validate

from conftest import ROOT


def test_runs_and_counts(tiny_config):
    doc, runs = run_experiment(tiny_config)
    assert doc["n_records"] == 2 * 3 * 4 and doc["n_failed"] == 0
    assert len(runs) == 2 and all(r["n_learner_arms"] == 12 for r in runs)
    assert doc["label"] == "exploratory" and "synthetic" in doc["simulation_notice"]


def test_byte_identical_reruns(tiny_config):
    a, _ = run_experiment(tiny_config)
    b, _ = run_experiment(copy.deepcopy(tiny_config))
    assert dump_result(a) == dump_result(b)


def test_execute_writes_valid_manifest(tiny_config, tmp_path):
    man = execute(tiny_config, tmp_path, "test")
    validate(man, "streak.manifest/1.0")
    payload = (tmp_path / "results.json").read_bytes()
    assert man["result_sha256"] == hashlib.sha256(payload).hexdigest()
    assert man["runtime_s"] >= 0 and man["versions"]["numpy"]
    assert len(man["config_hash"]) == 64


def test_errors_are_recorded_not_dropped(tiny_config, monkeypatch):
    real = runner.simulate_arm

    def flaky(h, av, u, arm, p):
        if arm.name == "A3":
            raise RuntimeError("injected failure")
        return real(h, av, u, arm, p)

    monkeypatch.setattr(runner, "simulate_arm", flaky)
    doc, runs = run_experiment(tiny_config)
    failed = [r for r in doc["records"] if r["status"] == "error"]
    assert len(failed) == 6 and doc["n_failed"] == 6 and doc["n_records"] == 24
    assert all("injected failure" in r["error"] and r["metrics"] is None for r in failed)
    assert sum(r["n_failed"] for r in runs) == 6


def test_cells_expand():
    for path, n in [("research/experiments/EXP-002/config.json", 27), ("research/experiments/EXP-003/config.json", 4),
                    ("research/experiments/EXP-001/config.json", 1)]:
        cells = expand_cells(json.loads((ROOT / path).read_text()))
        assert len(cells) == n
    c3 = expand_cells(json.loads((ROOT / "research/experiments/EXP-003/config.json").read_text()))
    assert {(c.params.form, c.params.gain_rule) for c in c3} == {
        ("exponential", "difficulty"), ("exponential", "flat"), ("power", "difficulty"), ("power", "flat")}


@pytest.mark.parametrize("exp", ["EXP-001", "EXP-002", "EXP-003"])
def test_confirmatory_refused_while_unfrozen(exp):
    cfg = json.loads((ROOT / f"research/experiments/{exp}/config.json").read_text())
    frozen, reason = protocol_freeze_status(exp, ROOT)
    assert not frozen and "not frozen" in reason.lower() or "NOT FROZEN" in reason
    with pytest.raises(GateError):
        run_experiment(cfg, root=ROOT)


def test_exploratory_with_confirmatory_seeds_refused(tiny_config):
    tiny_config["master_seeds"] = [1, 2]
    with pytest.raises(GateError):
        check_config(tiny_config)


def test_confirmatory_with_smoke_seeds_refused(tiny_config):
    tiny_config["label"] = "confirmatory"
    tiny_config["experiment_id"] = "EXP-001"
    with pytest.raises(ValueError):
        check_config(tiny_config)


def test_freeze_status_logic_on_a_copy(tmp_path):
    """Exercise the frozen branch on a temporary copy; the real protocols are not touched."""
    (tmp_path / "research" / "experiments" / "EXP-001").mkdir(parents=True)
    proto = tmp_path / "research" / "experiments" / "EXP-001" / "protocol.md"
    proto.write_text("frozen protocol text\n")
    (tmp_path / "research" / "protocol.md").write_text("Status: FROZEN by the owner\n")
    digest = hashlib.sha256(proto.read_bytes()).hexdigest()
    reg = tmp_path / "research" / "experiment_registry.csv"
    reg.write_text("exp_id,protocol_path,protocol_hash\n"
                   f"EXP-001,research/experiments/EXP-001/protocol.md,{digest}\n")
    assert protocol_freeze_status("EXP-001", tmp_path) == (True, "frozen")
    proto.write_text("edited after the freeze\n")
    assert protocol_freeze_status("EXP-001", tmp_path)[0] is False
    assert protocol_freeze_status("EXP-009", tmp_path)[0] is False


def test_git_dirty_ignores_untracked_files(tmp_path):
    import subprocess
    from streak.manifest import git_info
    g = ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=test-only"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "a.txt").write_text("a")
    subprocess.run(g + ["add", "a.txt"], check=True)
    subprocess.run(g + ["commit", "-qm", "init"], check=True)
    (tmp_path / "untracked.json").write_text("{}")
    rev, dirty = git_info(tmp_path)
    assert len(rev) == 40 and dirty is False
    (tmp_path / "a.txt").write_text("b")
    assert git_info(tmp_path)[1] is True
