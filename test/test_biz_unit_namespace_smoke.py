"""Smoke tests for Biz compact unit namespaces.

Verifies that `biz.biz_day`, `biz.work_day`, `biz.fis_qtr`, and `biz.fis_year`
support call and thru sugar.

Style: Arrange / Act / Assert (AA) per project `codeguide.md`.
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
def test_biz_unit_namespace_smoke():
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    biz = Biz(target_time=ref, ref_time=ref)

    # Act / Assert: iterate units and verify golden boolean expectations
    for unit in UNITS:
        ns = getattr(biz, unit)

        # Use a weekday ref for stable expectations
        weekday_ref = dt.datetime(2025, 3, 14, 12, 0, 0)  # Friday
        biz_wd = Biz(target_time=weekday_ref, ref_time=weekday_ref)
        ns_wd = getattr(biz_wd, unit)
        assert ns_wd.in_(0) is True
        assert ns_wd.in_(-1) is False
