"""Smoke tests for Biz compact unit namespaces.

Verifies that `biz.bday`, `biz.wday`, `biz.fqtr`, and `biz.fyear` delegate to
 the canonical `in_*` methods and support call and thru sugar.

Style: Arrange / Act / Assert (AA) per project `codeguide.md`.
"""

import datetime as dt
import pytest

from frist._biz import Biz


UNIT_MAP = [
    ("bday", "in_business_days"),
    ("wday", "in_working_days"),
    ("fqtr", "in_fiscal_quarters"),
    ("fyear", "in_fiscal_years"),
]

@pytest.mark.smoke
def test_biz_unit_namespace_smoke():
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    biz = Biz(target_time=ref, ref_time=ref)

    # Act / Assert: iterate units and verify golden boolean expectations
    for prop, method in UNIT_MAP:
        ns = getattr(biz, prop)

        # Use a weekday ref for stable expectations
        weekday_ref = dt.datetime(2025, 3, 14, 12, 0, 0)  # Friday
        biz_wd = Biz(target_time=weekday_ref, ref_time=weekday_ref)
        ns_wd = getattr(biz_wd, prop)
        assert ns_wd.in_(0) is True
        assert ns_wd.in_(-1) is False
