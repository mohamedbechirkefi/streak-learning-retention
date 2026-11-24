# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Forgetting-curve bounds, hand-computed values and update rules (protocol section 2)."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from streak.memory import recall, updated_half_life
from streak.params import ParameterError

FORMS = ["exponential", "power"]
delays = st.floats(min_value=0, max_value=1e4, allow_nan=False)
halfs = st.floats(min_value=1e-3, max_value=1e4, allow_nan=False)
UPD = dict(g_min=0.1, a=2.5, b=0.6, h_min=0.25)


def test_golden_exponential():
    assert recall(0, 2.0) == 1.0
    assert recall(2, 2.0) == pytest.approx(0.5)
    assert recall(4, 2.0) == pytest.approx(0.25)
    assert recall(30, 1.0) == pytest.approx(2.0 ** -30)


def test_golden_power():
    assert recall(0, 1.0, "power") == 1.0
    assert recall(1, 1.0, "power") == pytest.approx(0.5)  # (1 + 3)^-0.5
    assert recall(8 / 3, 1.0, "power") == pytest.approx(1 / 3)  # (1 + 8)^-0.5


@pytest.mark.parametrize("form", FORMS)
@given(d=delays, h=halfs)
def test_bounds(form, d, h):
    p = recall(d, h, form)
    assert 0.0 <= p <= 1.0


@pytest.mark.parametrize("form", FORMS)
@given(d1=delays, d2=delays, h=halfs)
def test_non_increasing_in_delay(form, d1, d2, h):
    lo, hi = sorted([d1, d2])
    assert recall(hi, h, form) <= recall(lo, h, form)


@pytest.mark.parametrize("form", FORMS)
@given(d=delays, h1=halfs, h2=halfs)
def test_non_decreasing_in_half_life(form, d, h1, h2):
    lo, hi = sorted([h1, h2])
    assert recall(d, lo, form) <= recall(d, hi, form) + 1e-15


@pytest.mark.parametrize("form", FORMS)
@given(h=halfs)
def test_half_at_half_life(form, h):
    assert recall(h, h, form) == pytest.approx(0.5, rel=1e-9)


def test_power_decays_slower_than_exponential_at_long_delays():
    assert recall(10, 1.0, "power") > recall(10, 1.0, "exponential")


def test_vectorised_matches_scalar():
    d = np.array([0.0, 1.0, 5.0])
    h = np.array([1.0, 2.0, 0.5])
    for form in FORMS:
        v = recall(d, h, form)
        assert v.shape == (3,)
        assert [recall(x, y, form) for x, y in zip(d, h)] == pytest.approx(list(v))


@pytest.mark.parametrize("bad", [(-1, 1.0), (1, 0.0), (1, -2.0), (math.nan, 1.0), (1, math.inf)])
def test_recall_invalid_inputs(bad):
    with pytest.raises(ParameterError):
        recall(*bad)


def test_recall_unknown_form():
    with pytest.raises(ParameterError):
        recall(1, 1, "hyperbolic")


def test_update_golden():
    assert updated_half_life(1.0, 0.5, True, gain_rule="difficulty", **UPD) == pytest.approx(2.35)
    assert updated_half_life(1.0, 0.9, True, gain_rule="difficulty", **UPD) == pytest.approx(1.35)
    assert updated_half_life(1.0, 0.5, True, gain_rule="flat", **UPD) == pytest.approx(1.85)
    assert updated_half_life(1.0, 0.5, False, gain_rule="difficulty", **UPD) == pytest.approx(0.6)
    assert updated_half_life(0.3, 0.5, False, gain_rule="flat", **UPD) == pytest.approx(0.25)  # floor
    assert updated_half_life(0.1, 0.5, False, gain_rule="difficulty", **UPD) == pytest.approx(0.25)  # raised to floor


def test_flat_gain_equals_difficulty_gain_at_p_07():
    a = updated_half_life(2.0, 0.7, True, gain_rule="difficulty", **UPD)
    b = updated_half_life(2.0, 0.7, True, gain_rule="flat", **UPD)
    assert a == pytest.approx(b)


@given(h=halfs, p=st.floats(0, 1), q=st.floats(0, 1))
def test_difficulty_gain_decreases_with_recall(h, p, q):
    lo, hi = sorted([p, q])
    g_lo = updated_half_life(h, lo, True, gain_rule="difficulty", **UPD)
    g_hi = updated_half_life(h, hi, True, gain_rule="difficulty", **UPD)
    assert g_hi <= g_lo * (1 + 1e-12)


@given(h=halfs, p=st.floats(0, 1))
@settings(max_examples=200)
def test_success_increases_failure_follows_rule(h, p):
    for rule in ("difficulty", "flat"):
        assert updated_half_life(h, p, True, gain_rule=rule, **UPD) > h
        assert updated_half_life(h, p, False, gain_rule=rule, **UPD) == pytest.approx(max(0.25, 0.6 * h))


@pytest.mark.parametrize("h,p", [(0.0, 0.5), (-1.0, 0.5), (1.0, 1.5), (1.0, -0.1), (1.0, math.nan)])
def test_update_invalid(h, p):
    with pytest.raises(ParameterError):
        updated_half_life(h, p, True, gain_rule="difficulty", **UPD)


def test_update_unknown_rule():
    with pytest.raises(ParameterError):
        updated_half_life(1.0, 0.5, True, gain_rule="linear", **UPD)
