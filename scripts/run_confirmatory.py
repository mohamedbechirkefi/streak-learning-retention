# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Run one frozen confirmatory experiment through the CLI run guard and capture provenance.

Checks before the run: tracked tree clean, freeze-record hashes equal the files on disk,
raw Duolingo file SHA-256 equal to the data manifest. Then runs
``nice -n 10 python -m streak.cli run --config <frozen config> --out results/confirmatory/<EXP>``
as a subprocess, logs stdout and stderr, and writes ``provenance.json`` (one record per run:
id, config hash, seed, revision, data manifest hash, hardware, start and end time, exit status)
and ``sha256_manifest.json`` (SHA-256 of every output file). Per-run start and end times are
derived from the experiment start time plus the runner's cumulative per-run runtimes (the
runner executes runs sequentially) and are labelled as derived.

Usage: .venv/bin/python scripts/run_confirmatory.py EXP-001
"""

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def preflight(exp: str) -> dict:
    rec = json.loads((ROOT / "research" / "freeze.json").read_text())
    checks = {"tracked_tree_clean": git("status", "--porcelain", "--untracked-files=no") == ""}
    checks["protocol"] = sha(ROOT / rec["protocol_path"]) == rec["protocol_sha256"]
    checks["data_manifest"] = sha(ROOT / rec["data_manifest_path"]) == rec["data_manifest_sha256"]
    e = rec["experiments"][exp]
    checks["exp_protocol"] = sha(ROOT / e["protocol_path"]) == e["protocol_sha256"]
    checks["exp_config"] = sha(ROOT / e["config_path"]) == e["config_file_sha256"]
    raw = ROOT / "data" / "raw" / "settles.acl16.learning_traces.13m.csv.gz"
    checks["raw_data"] = raw.exists() and sha(raw) == rec["raw_data_sha256"]
    return {"checks": checks, "ok": all(checks.values()), "freeze": rec, "exp": e}


def main() -> int:
    exp = sys.argv[1]
    pre = preflight(exp)
    print(json.dumps(pre["checks"]))
    if not pre["ok"]:
        print("preflight failed: not running", file=sys.stderr)
        return 4
    out = ROOT / "results" / "confirmatory" / exp
    out.mkdir(parents=True, exist_ok=True)
    cmd = ["nice", "-n", "10", sys.executable, "-m", "streak.cli", "run", "--config", pre["exp"]["config_path"],
           "--out", str(out.relative_to(ROOT))]
    revision = git("rev-parse", "HEAD")
    started = datetime.now(timezone.utc)
    with open(out / "run.log", "w") as log:
        proc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    finished = datetime.now(timezone.utc)
    man_path = out / "run_manifest.json"
    man = json.loads(man_path.read_text()) if man_path.exists() else None
    hardware = (man or {}).get("platform") or {"os": platform.system(), "machine": platform.machine()}
    runs, t = [], started
    for r in (man or {}).get("runs", []):
        end = t + timedelta(seconds=r["runtime_s"])
        runs.append({"run_id": r["run_id"], "cell_id": r["cell_id"], "seed": r["master_seed"],
                     "config_hash": man["config_hash"], "revision": revision,
                     "data_manifest_sha256": pre["freeze"]["data_manifest_sha256"], "hardware": hardware,
                     "start_utc_derived": t.isoformat(timespec="milliseconds"),
                     "end_utc_derived": end.isoformat(timespec="milliseconds"),
                     "runtime_s": r["runtime_s"], "n_learner_arms": r["n_learner_arms"], "n_failed": r["n_failed"],
                     "exit_status": "ok" if proc.returncode == 0 and r["n_failed"] == 0 else
                                    ("learner-arm failures recorded" if r["n_failed"] else "process failed")})
        t = end
    prov = {"experiment_id": exp, "label": "confirmatory", "command": " ".join(cmd), "revision": revision,
            "preflight": pre["checks"], "config_path": pre["exp"]["config_path"],
            "config_canonical_sha256": pre["exp"]["config_canonical_sha256"],
            "data_manifest_sha256": pre["freeze"]["data_manifest_sha256"],
            "raw_data_sha256": pre["freeze"]["raw_data_sha256"],
            "started_utc": started.isoformat(timespec="seconds"), "finished_utc": finished.isoformat(timespec="seconds"),
            "wall_clock_s": round((finished - started).total_seconds(), 3), "process_exit_code": proc.returncode,
            "n_runs": len(runs), "runs": runs,
            "note": "start_utc_derived and end_utc_derived: experiment start plus cumulative runner runtimes."}
    (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "sha256_manifest.json")
    (out / "sha256_manifest.json").write_text(json.dumps(
        {str(p.relative_to(ROOT)): {"sha256": sha(p), "bytes": p.stat().st_size} for p in files}, indent=2) + "\n")
    print(f"exit {proc.returncode}; {len(runs)} runs; wall clock {prov['wall_clock_s']} s")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
