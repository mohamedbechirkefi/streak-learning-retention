# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Experiment runner: validated config -> learner-arm simulations -> validated result file
and run manifest.

Gate (G-FREEZE): a confirmatory config is refused unless the experiment's protocol
is frozen, i.e. its row in research/experiment_registry.csv carries a SHA-256 hash
that equals the hash of the protocol file on disk, and research/protocol.md is no
longer marked "NOT FROZEN". Exploratory configs may only use the smoke seed range.
"""

from __future__ import annotations

import csv
import itertools
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import ENGINE_VERSION, __version__
from .manifest import (canonical_json, environment, git_info, peak_memory_bytes, repo_root,
                       sha256_bytes, sha256_file)
from .metrics import learner_arm_metrics
from .params import ModelParams, get_arm
from .population import SMOKE_SEED_RANGE, generate_learners
from .schema import validate
from .simulate import simulate_arm

SIMULATION_NOTICE = ("Simulation of synthetic learners. Not evidence about real human learning, "
                     "motivation or any real product.")


class GateError(RuntimeError):
    """Raised when a run would cross a gate (confirmatory run on an unfrozen protocol)."""


def load_config(path: Path) -> dict:
    cfg = json.loads(Path(path).read_text())
    check_config(cfg)
    return cfg


def check_config(cfg: dict) -> None:
    validate(cfg, "streak.config/1.0")
    ModelParams.from_dict(cfg["base_params"])  # raises ParameterError if invalid
    for arm in cfg["arms"]:
        get_arm(arm)
    an = cfg["analysis"]
    for pair in [an["primary_contrast"], *an["secondary_contrasts"]]:
        for arm in pair:
            if arm not in cfg["arms"]:
                raise ValueError(f"contrast arm {arm!r} is not among the config arms")
    seeds = cfg["master_seeds"]
    if len(set(seeds)) != len(seeds):
        raise ValueError("master_seeds must be distinct")
    smoke = [s in SMOKE_SEED_RANGE for s in seeds]
    if cfg["label"] == "exploratory" and not all(smoke):
        raise GateError("exploratory configs may only use smoke seeds 9001 to 9999 "
                        "(confirmatory seeds are reserved until the protocol is frozen)")
    if cfg["label"] == "confirmatory":
        if any(smoke):
            raise ValueError("confirmatory configs must not use smoke seeds")
        if not re.fullmatch(r"EXP-[0-9]{3}", cfg["experiment_id"]):
            raise ValueError("confirmatory configs need a registered EXP-NNN id")


def config_hash(cfg: dict) -> str:
    return sha256_bytes(canonical_json(cfg))


def protocol_freeze_status(experiment_id: str, root: Path | None = None) -> tuple[bool, str]:
    """(frozen, reason). Frozen only if the registry hash matches the protocol file on disk
    and the parent protocol is no longer marked as not frozen."""
    root = root or repo_root()
    reg = root / "research" / "experiment_registry.csv"
    if not reg.exists():
        return False, f"registry not found: {reg}"
    with open(reg, newline="") as f:
        rows = {r["exp_id"]: r for r in csv.DictReader(f)}
    row = rows.get(experiment_id)
    if row is None:
        return False, f"{experiment_id} is not registered"
    recorded = row.get("protocol_hash", "").strip()
    if not re.fullmatch(r"[0-9a-f]{64}", recorded):
        return False, f"{experiment_id} protocol has no recorded hash ({recorded!r}): not frozen"
    proto = root / row["protocol_path"]
    if not proto.exists() or sha256_file(proto) != recorded:
        return False, f"{experiment_id} protocol on disk does not match the recorded hash"
    parent = root / "research" / "protocol.md"
    if "NOT FROZEN" in parent.read_text():
        return False, "research/protocol.md is marked NOT FROZEN"
    return True, "frozen"


def require_runnable(cfg: dict, root: Path | None = None) -> None:
    check_config(cfg)
    if cfg["label"] == "confirmatory":
        frozen, reason = protocol_freeze_status(cfg["experiment_id"], root)
        if not frozen:
            raise GateError(f"refusing confirmatory run of {cfg['experiment_id']}: {reason}. "
                            "Freezing is the owner's decision (G-FREEZE).")


def _fmt(v: float) -> str:
    return f"{v:g}"


@dataclass(frozen=True)
class Cell:
    cell_id: str
    params: ModelParams


def expand_cells(cfg: dict) -> list[Cell]:
    """Grid (h0 x a x q) times model variants; a single 'default' cell if neither is given."""
    base = ModelParams.from_dict(cfg["base_params"])
    grid = cfg.get("grid") or {}
    keys = [k for k in ("h0", "a", "q") if k in grid]
    variants = cfg.get("model_variants") or [None]
    cells = []
    for values in itertools.product(*[grid[k] for k in keys]):
        for var in variants:
            upd = dict(zip(keys, values))
            parts = [f"{k}={_fmt(v)}" for k, v in upd.items()]
            if var is not None:
                upd.update(var)
                parts.append(f"{var['form'][:3]}-{var['gain_rule'][:4]}")
            cells.append(Cell("|".join(parts) or "default", base.with_updates(**upd)))
    ids = [c.cell_id for c in cells]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate cells in grid or model variants")
    return cells


def run_id(experiment_id: str, cell_id: str, seed: int) -> str:
    return f"{experiment_id}/{cell_id}/s{seed}"


def run_experiment(cfg: dict, *, root: Path | None = None) -> tuple[dict, list[dict]]:
    """Run every (cell, master seed, learner, arm). Errors are recorded per learner-arm,
    never dropped. Returns (result document, per-run timing records)."""
    require_runnable(cfg, root)
    cells = expand_cells(cfg)
    records: list[dict] = []
    runs: list[dict] = []
    n_learners = cfg["learners_per_seed"]
    for cell in cells:
        for seed in cfg["master_seeds"]:
            t0 = time.perf_counter()
            learners = generate_learners(seed, n_learners, cell.params)
            rid = run_id(cfg["experiment_id"], cell.cell_id, seed)
            n_failed = 0
            for lr in learners:
                h_init = lr.initial_half_lives(cell.params)
                avail = lr.availability(cell.params)
                for arm_name in cfg["arms"]:
                    rec = {"run_id": rid, "cell_id": cell.cell_id, "master_seed": seed,
                           "learner_index": lr.learner_index, "arm": arm_name,
                           "status": "ok", "error": None, "metrics": None}
                    try:
                        res = simulate_arm(h_init, avail, lr.outcome_u, get_arm(arm_name), cell.params)
                        rec["metrics"] = learner_arm_metrics(res, cell.params)
                    except Exception as exc:  # recorded, never dropped silently
                        rec["status"] = "error"
                        rec["error"] = f"{type(exc).__name__}: {exc}"
                        n_failed += 1
                    records.append(rec)
            runs.append({"run_id": rid, "cell_id": cell.cell_id, "master_seed": seed,
                         "n_learner_arms": n_learners * len(cfg["arms"]), "n_failed": n_failed,
                         "runtime_s": round(time.perf_counter() - t0, 6)})
    doc = {
        "schema_version": "streak.result/1.0",
        "experiment_id": cfg["experiment_id"],
        "label": cfg["label"],
        "simulation_notice": SIMULATION_NOTICE,
        "protocol_version": cfg["protocol_version"],
        "config_hash": config_hash(cfg),
        "engine_version": ENGINE_VERSION,
        "package_version": __version__,
        "config": cfg,
        "cells": [{"cell_id": c.cell_id, "params": c.params.to_dict()} for c in cells],
        "records": records,
        "n_records": len(records),
        "n_failed": sum(r["status"] == "error" for r in records),
    }
    validate(doc, "streak.result/1.0")
    return doc, runs


def dump_result(doc: dict) -> bytes:
    """Deterministic serialisation (no timestamps in the result file)."""
    return (json.dumps(doc, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def load_result(path: Path) -> dict:
    doc = json.loads(Path(path).read_text())
    validate(doc, "streak.result/1.0")
    if doc["n_records"] != len(doc["records"]):
        raise ValueError("n_records does not match the number of records")
    return doc


def execute(cfg: dict, out_dir: Path, command: str, root: Path | None = None) -> dict:
    """Run, validate, write results.json and run_manifest.json into out_dir. Returns the manifest."""
    root = root or repo_root()
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    doc, runs = run_experiment(cfg, root=root)
    runtime = time.perf_counter() - t0
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "results.json"
    payload = dump_result(doc)
    result_path.write_bytes(payload)
    rev, dirty = git_info(root)
    env = environment()
    try:
        rel = str(result_path.resolve().relative_to(root.resolve()))
    except ValueError:
        rel = str(result_path)
    manifest = {
        "schema_version": "streak.manifest/1.0",
        "experiment_id": cfg["experiment_id"],
        "label": cfg["label"],
        "config_hash": doc["config_hash"],
        "master_seeds": cfg["master_seeds"],
        "git_revision": rev,
        "git_dirty": dirty,
        "versions": env["versions"],
        "platform": env["platform"],
        "started_utc": started.isoformat(timespec="seconds"),
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runtime_s": round(runtime, 3),
        "peak_memory_bytes": peak_memory_bytes(),
        "runs": runs,
        "result_path": rel,
        "result_sha256": sha256_bytes(payload),
        "command": command,
    }
    validate(manifest, "streak.manifest/1.0")
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
