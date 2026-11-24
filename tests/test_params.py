# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Parameter validation and arm definitions."""

import pytest

from streak.params import ARMS, ArmSpec, ModelParams, ParameterError, get_arm


def test_defaults_match_protocol_section_10():
    p = ModelParams()
    assert (p.n_items, p.horizon_days, p.budget_slots, p.slot_minutes, p.daily_cap_slots) == (100, 56, 672, 0.5, 60)
    assert (p.g_min, p.a, p.b, p.h_min, p.h0, p.q) == (0.1, 2.5, 0.6, 0.25, 1.0, 0.85)
    assert p.retention_delays == (1, 7, 30, 90)
    assert p.g_flat == pytest.approx(0.85)
    assert p.budget_slots * p.slot_minutes == 336  # minutes per learner


@pytest.mark.parametrize("kw", [
    {"q": 1.1}, {"q": -0.1}, {"b": 1.0}, {"b": 0.0}, {"h0": 0.0}, {"h_min": -1.0},
    {"n_items": 0}, {"horizon_days": -3}, {"daily_cap_slots": 0}, {"budget_slots": -1},
    {"form": "linear"}, {"gain_rule": "none"}, {"retention_delays": (1, 7)},
    {"fixed_weekdays": (1, 1)}, {"fixed_weekdays": (7,)}, {"fixed_weekdays": ()},
    {"slot_minutes": float("nan")}, {"n_items": 2.5}, {"sigma_item": -0.1},
])
def test_invalid_params_raise(kw):
    with pytest.raises(ParameterError):
        ModelParams(**kw)


def test_round_trip_dict():
    p = ModelParams(h0=2.0, form="power")
    assert ModelParams.from_dict(p.to_dict()) == p


def test_unknown_key_rejected():
    with pytest.raises(ParameterError):
        ModelParams.from_dict({"h00": 1.0})


def test_arms():
    assert get_arm("A1") == ArmSpec("A1", "fixed", "round_robin")
    assert get_arm("A2").timing == get_arm("A3").timing == "daily"
    assert {a.selection for a in ARMS.values()} >= {"round_robin", "easiest", "due_threshold"}
    # Protocol section 14.5: the retired draft rule is used by no arm.
    assert "most_due" not in {a.selection for a in ARMS.values()}
    assert get_arm("A3").selection == get_arm("F-DUE").selection == "due_threshold"
    with pytest.raises(ParameterError):
        get_arm("A9")
    with pytest.raises(ParameterError):
        ArmSpec("X", "none", "easiest")
    with pytest.raises(ParameterError):
        ArmSpec("X", "weekly", "easiest")
