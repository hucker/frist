"""
Smoke tests for UnitNamespace.between single-unit behavior.

Ensures that between(start, None, mode) always maps to in_(start, start+1)
for all inclusive modes: "both", "left", "right", and "neither".
"""

import datetime as dt

import pytest

from frist._frist import Cal


@pytest.mark.parametrize("mode", ["both", "left", "right", "neither"])
def test_between_single_unit_maps_to_in(mode: str) -> None:
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
