"""Smoke tests for Biz compact unit namespaces.

Verifies that `biz.bday`, `biz.wday`, `biz.fqtr`, and `biz.fyr` delegate to
 the canonical `in_*` methods and support call and thru sugar.

Style: Arrange / Act / Assert (AA) per project `codeguide.md`.
"""

import datetime as dt

from frist._biz import Biz


UNIT_MAP = [
    ("bday", "in_business_days"),
    ("wday", "in_working_days"),
    ("fqtr", "in_fiscal_quarters"),
    ("fyr", "in_fiscal_years"),
]


def test_biz_unit_namespace_smoke():
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    biz = Biz(target_time=ref, ref_time=ref)

    # Act / Assert: iterate units and compare compact namespace to canonical
    for prop, method in UNIT_MAP:
        ns = getattr(biz, prop)
        direct = getattr(biz, method)

        # current unit equality
        assert ns.in_(0) == direct(0)

        # single-arg negative
        assert ns.in_(-1) == direct(-1)

        # __call__ maps to in_
        assert ns(-1, 0) == ns.in_(-1, 0)

        # inclusive 'thru' should map to half-open by advancing the end
        if hasattr(ns, "thru"):
            assert ns.thru(-1, 0) == ns.in_(-1, 1)

        # Add one golden boolean check per unit using a weekday ref so expectations
        # are independent of the initial `ref` used for the parity checks above.
        weekday_ref = dt.datetime(2025, 3, 14, 12, 0, 0)  # 2025-03-14 is a Friday
        biz_wd = Biz(target_time=weekday_ref, ref_time=weekday_ref)
        ns_wd = getattr(biz_wd, prop)
        assert ns_wd.in_(0) is True
        assert ns_wd.in_(-1) is False
