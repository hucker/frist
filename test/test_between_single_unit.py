"""
Smoke tests for UnitNamespace.between single-unit behavior.

Ensures that between(start, None, mode) maps to a single-unit window shifted
by inclusivity:
- both/left: `adj_start = start`, window `[start, start+1)`
- right/neither: `adj_start = start+1`, window `[start+1, start+2)`
"""

import datetime as dt

import pytest

from frist._frist import Cal


@pytest.mark.parametrize("mode", ["both", "left"])
def test_between_single_unit_maps_to_in_left_both(mode: str) -> None:
    ref = dt.datetime(2025, 11, 20, 12, 0, 0)
    # Choose a target that exactly matches start window
    target = dt.datetime(2025, 11, 20, 12, 0, 0)
    c = Cal(target_dt=target, ref_dt=ref)

    # Hour namespace: start=0 represents the current hour window
    assert c.hour.between(0, None, mode) == c.hour.in_(0, 1)

    # Day namespace: start=0 represents the current day window
    assert c.day.between(0, None, mode) == c.day.in_(0, 1)

    # Month namespace: start=0 represents the current month window
    assert c.month.between(0, None, mode) == c.month.in_(0, 1)


@pytest.mark.parametrize("mode", ["right", "neither"])
def test_between_single_unit_maps_to_in_right_neither(mode: str) -> None:
    ref = dt.datetime(2025, 11, 20, 12, 0, 0)
    # Target at the boundary such that shifting start matters
    target = dt.datetime(2025, 11, 20, 12, 0, 0)
    c = Cal(target_dt=target, ref_dt=ref)

    # Hour namespace: `adj_start = start + 1` when end=None for right/neither
    assert c.hour.between(0, None, mode) == c.hour.in_(1, 2)

    # Day namespace
    assert c.day.between(0, None, mode) == c.day.in_(1, 2)

    # Month namespace
    assert c.month.between(0, None, mode) == c.month.in_(1, 2)
