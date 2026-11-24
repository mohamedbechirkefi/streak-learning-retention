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


def test_cli_run_refuses_changed_confirmatory_config(capsys, tmp_path):
    # Never run a frozen confirmatory config from the test suite (no unscheduled confirmatory run):
    # only a changed copy is passed to the CLI, which must refuse it before simulating anything.
    cfg = json.loads((ROOT / "research/experiments/EXP-001/config.json").read_text())
    cfg["base_params"]["h0"] = 1.0
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(cfg))
    rc = main(["run", "--config", str(path), "--out", str(tmp_path / "out")])
    assert rc == 3
    err = capsys.readouterr().err
    assert "G-FREEZE" in err and "differs from the frozen config" in err
    assert not (tmp_path / "out").exists()


def test_cli_smoke_rejects_confirmatory_config(capsys):
    assert main(["smoke", "--config", str(ROOT / "research/experiments/EXP-001/config.json")]) == 2


def test_cli_smoke_and_report(tiny_config, tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(tiny_config))
    assert main(["smoke", "--config", str(cfg), "--out", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "report" / "report.md").exists()
    assert main(["report", "--results", str(tmp_path / "out" / "results.json"), "--out", str(tmp_path / "r2")]) == 0
    assert (tmp_path / "r2" / "contrasts.csv").exists()


def test_holm_primary_across_cells(tiny_config):
    """Protocol section 14.6: optional Holm adjustment of the primary contrast across cells."""
    from streak.report import analyse
    from streak.runner import run_experiment
    from streak.stats import holm_adjust
    cfg = dict(tiny_config, grid={"q": [0.7, 1.0]})
    cfg["analysis"] = dict(cfg["analysis"], holm_primary_across_cells=True)
    doc, _ = run_experiment(cfg)
    out = analyse(doc)
    prim = [c["primary"] for c in out["cells"]]
    assert len(prim) == 2
    assert [p["p_holm"] for p in prim] == holm_adjust([p["p_boot"] for p in prim])
    for p in prim:
        assert p["relevant_holm_across_cells"] == (p["classification"].startswith("relevant") and p["p_holm"] < 0.05)
    # Without the flag the primary rows carry no Holm value.
    doc2, _ = run_experiment(tiny_config)
    assert "p_holm" not in analyse(doc2)["cells"][0]["primary"]
