"""Smoke tests for the compact unit namespace API.

These tests verify the ergonomic `cal.<unit>` namespace (compact form)
delegates to the canonical `Cal.in_*` methods and supports call, slice
and inclusive `thru` sugar.

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
    ("yr", "in_years"),
]


def test_unit_namespace_smoke():
    """Smoke test for compact unit namespaces.

    Verifies that each compact namespace delegates to the canonical
    `in_*` behavior and supports call/slice/thru sugar.
    """
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    cal = Cal(target_dt=ref, ref_dt=ref)

    # Act / Assert: iterate units and compare compact namespace to canonical
    for prop, method in UNIT_MAP:
        # Act
        ns = getattr(cal, prop)
        direct = getattr(cal, method)

        # Assert: current unit equality
        assert ns.in_(0) == direct(0)

        # Assert: single-arg negative
        assert ns.in_(-1) == direct(-1)

        # Assert: __call__ maps to in_
        assert ns(-1, 0) == ns.in_(-1, 0)

        # Assert: slice sugar
        assert ns[-1:0] == ns.in_(-1, 0)

        # Assert: inclusive 'thru' should map to half-open by advancing the end
        if hasattr(ns, "thru"):
            assert ns.thru(-1, 0) == ns.in_(-1, 1)
            assert ns.thru[-1:0] == ns.in_(-1, 1)
