"""Smoke tests for Biz compact unit units.

Verifies that `biz.biz_day`, `biz.work_day`, `biz.fis_qtr`, and `biz.fis_year`
support call and thru sugar.

Style: Arrange / Act / Assert (AA) per project `CODESTYLE.md`.
"""

import datetime as dt

import pytest

from frist._biz import Biz

UNITS = [
    "biz_day",
    "work_day",
    "fis_qtr",
    "fis_year",
]

@pytest.mark.smoke
def test_biz_unit_unit_smoke():
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    biz = Biz(target_dt=ref, ref_dt=ref)

    # Act / Assert: iterate units and verify golden boolean expectations
    for unit in UNITS:
        ns = getattr(biz, unit)

        # Use a weekday ref for stable expectations
        weekday_ref = dt.datetime(2025, 3, 14, 12, 0, 0)  # Friday
        biz_wd = Biz(target_dt=weekday_ref, ref_dt=weekday_ref)
        ns_wd = getattr(biz_wd, unit)
        assert ns_wd.in_(0) is True
        assert ns_wd.in_(-1) is False
