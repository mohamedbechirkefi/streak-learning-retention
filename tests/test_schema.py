# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Versioned JSON schemas: valid documents pass, malformed ones fail closed."""

import copy
import json

import pytest

from streak.schema import SchemaError, validate, validation_errors

from conftest import ROOT

CONFIGS = ["experiments/smoke-exp001.json", "experiments/smoke-exp001-n200.json", "experiments/smoke-exp002.json",
           "experiments/smoke-exp003.json", "research/experiments/EXP-001/config.json",
           "research/experiments/EXP-002/config.json", "research/experiments/EXP-003/config.json"]


@pytest.mark.parametrize("path", CONFIGS)
def test_committed_configs_valid(path):
    validate(json.loads((ROOT / path).read_text()), "streak.config/1.0")


def test_confirmatory_configs_match_protocol_matrix():
    seeds = [1, 2, 3, 4, 5]
    c1 = json.loads((ROOT / "research/experiments/EXP-001/config.json").read_text())
    c2 = json.loads((ROOT / "research/experiments/EXP-002/config.json").read_text())
    c3 = json.loads((ROOT / "research/experiments/EXP-003/config.json").read_text())
    assert c1["master_seeds"] == c2["master_seeds"] == c3["master_seeds"] == seeds
    assert (c1["learners_per_seed"], len(c1["arms"])) == (200, 4)
    assert c2["learners_per_seed"] == 100 and len(c2["grid"]["h0"]) * len(c2["grid"]["a"]) * len(c2["grid"]["q"]) == 27
    assert c3["learners_per_seed"] == 100 and len(c3["arms"]) == 6 and len(c3["model_variants"]) == 4
    assert all(c["analysis"]["primary_contrast"] == ["A2", "A1"] for c in (c1, c2, c3))


@pytest.mark.parametrize("mutate", [
    lambda c: c.pop("label"),
    lambda c: c.update(label="final"),
    lambda c: c.update(schema_version="streak.config/0.9"),
    lambda c: c.update(learners_per_seed=0),
    lambda c: c.update(learners_per_seed="20"),
    lambda c: c.update(extra=1),
    lambda c: c.update(arms=["A7"]),
    lambda c: c["analysis"].update(sesoi=float("nan")),
    lambda c: c.update(experiment_id="exp-1"),
])
def test_malformed_config_rejected(mutate):
    c = json.loads((ROOT / CONFIGS[0]).read_text())
    mutate(c)
    with pytest.raises(SchemaError):
        validate(c, "streak.config/1.0")


def test_unknown_schema():
    with pytest.raises(SchemaError):
        validate({}, "streak.unknown/1.0")


def test_result_metric_bounds_enforced(tiny_config):
    from streak.runner import run_experiment
    doc, _ = run_experiment(tiny_config)
    validate(doc, "streak.result/1.0")
    bad = copy.deepcopy(doc)
    bad["records"][0]["metrics"]["R30"] = 1.5
    assert any("maximum" in e for e in validation_errors(bad, "streak.result/1.0"))
    bad = copy.deepcopy(doc)
    del bad["records"][0]["metrics"]["R30"]
    with pytest.raises(SchemaError):
        validate(bad, "streak.result/1.0")
