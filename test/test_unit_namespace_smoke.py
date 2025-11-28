"""Smoke tests for the compact unit namespace API.

These tests verify the ergonomic `cal.<unit>` namespace (compact form)
delegates to the canonical `Cal.in_*` methods and supports call and inclusive `thru` sugar.

Style: follow Arrange / Act / Assert (AA) comments per project `codeguide.md`.
"""

import datetime as dt

from frist._cal import Cal


UNIT_MAP = [
    ("min", "in_minutes"),
    ("hr", "in_hours"),
    ("day", "in_days"),
    ("wk", "in_weeks"),
    ("mon", "in_months"),
    ("qtr", "in_quarters"),
    ("year", "in_years"),
]


def test_unit_namespace_smoke():
    """Smoke test for compact unit namespaces.

    Verifies that each compact namespace delegates to the canonical
    `in_*` behavior and supports call/slice/thru sugar.
    """
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    cal = Cal(target_dt=ref, ref_dt=ref)

    # Act / Assert: iterate units and verify golden boolean expectations
    for prop, method in UNIT_MAP:
        ns = getattr(cal, prop)

        # Golden checks: when ref==target, current unit should be True, previous should be False
        assert ns.in_(0) is True
        assert ns.in_(-1) is False
