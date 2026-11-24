# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Report generator and CLI: outputs computed from results, malformed results rejected."""

import csv
import json
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from streak.cli import main
from streak.report import build_report
from streak.runner import execute
from streak.schema import SchemaError

from conftest import ROOT


@pytest.fixture
def run_dir(tiny_config, tmp_path):
    execute(tiny_config, tmp_path, "test")
    return tmp_path


def test_report_numbers_come_from_records(run_dir):
    written = build_report(run_dir / "results.json", run_dir / "report")
    doc = json.loads((run_dir / "results.json").read_text())
    analysis = json.loads(written["analysis"].read_text())
    for arm in analysis["cells"][0]["arms"]:
        r30 = [r["metrics"]["R30"] for r in doc["records"] if r["arm"] == arm["arm"]]
        assert arm["metrics"]["R30"]["mean"] == pytest.approx(np.mean(r30))
    by = {(r["master_seed"], r["learner_index"], r["arm"]): r["metrics"]["R30"] for r in doc["records"]}
    diffs = [by[(s, j, "A2")] - by[(s, j, "A1")] for (s, j, a) in by if a == "A2"]
    assert analysis["cells"][0]["primary"]["mean_diff"] == pytest.approx(np.mean(diffs))
    rows = list(csv.DictReader(open(written["metrics"])))
    assert {r["arm"] for r in rows} == {"A0", "A1", "A2", "A3"}
    md = written["report_md"].read_text()
    assert "EXPLORATORY" in md and chr(0x2014) not in md
    for svg in (run_dir / "report" / "figures").glob("*.svg"):
        root = ET.parse(svg).getroot()
        assert root.find("{http://www.w3.org/2000/svg}title") is not None


def test_malformed_result_rejected(run_dir):
    doc = json.loads((run_dir / "results.json").read_text())
    doc["records"][0]["status"] = "maybe"
    bad = run_dir / "bad.json"
    bad.write_text(json.dumps(doc))
    with pytest.raises(SchemaError):
        build_report(bad, run_dir / "bad-report")
    doc = json.loads((run_dir / "results.json").read_text())
    doc["n_records"] += 1
    bad.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        build_report(bad, run_dir / "bad-report")


def test_cli_run_refuses_confirmatory(capsys):
    rc = main(["run", "--config", str(ROOT / "research/experiments/EXP-001/config.json"), "--out", "/nonexistent/x"])
    assert rc == 3
    assert "G-FREEZE" in capsys.readouterr().err


def test_cli_smoke_rejects_confirmatory_config(capsys):
    assert main(["smoke", "--config", str(ROOT / "research/experiments/EXP-001/config.json")]) == 2


def test_cli_smoke_and_report(tiny_config, tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(tiny_config))
    assert main(["smoke", "--config", str(cfg), "--out", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "report" / "report.md").exists()
    assert main(["report", "--results", str(tmp_path / "out" / "results.json"), "--out", str(tmp_path / "r2")]) == 0
    assert (tmp_path / "r2" / "contrasts.csv").exists()
