# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Shared fixtures for the STREAK test suite."""

import copy
import json
from pathlib import Path

import pytest

from streak.params import ModelParams

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def small_params():
    """K = 10 items, T = 14 days, M = 42 slots (divisible by 14 daily and 6 fixed days)."""
    return ModelParams(n_items=10, horizon_days=14, budget_slots=42, daily_cap_slots=5)


@pytest.fixture
def tiny_config():
    """A small exploratory config derived from the committed smoke config."""
    cfg = json.loads((ROOT / "experiments" / "smoke-exp001.json").read_text())
    cfg = copy.deepcopy(cfg)
    cfg["experiment_id"] = "SMOKE-TEST"
    cfg["master_seeds"] = [9001, 9002]
    cfg["learners_per_seed"] = 3
    cfg["base_params"].update(n_items=10, horizon_days=14, budget_slots=42, daily_cap_slots=5)
    cfg["analysis"]["bootstrap_resamples"] = 200
    return cfg
