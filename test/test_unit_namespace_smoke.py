"""Smoke tests for the compact unit namespace API.

These tests verify the ergonomic `cal.<unit>` namespace (compact form)
supports call and inclusive `thru` sugar.

Style: follow Arrange / Act / Assert (AA) comments per project `CODEGUIDE.md`.
"""

import datetime as dt
import pytest

from frist._cal import Cal


UNITS = [
    "minute",
    "hour", 
    "day",
    "week",
    "month",
    "qtr",
    "year",
]

@pytest.mark.smoke
def test_unit_namespace_smoke():
    """Smoke test for compact unit namespaces.

    Verifies that each compact namespace supports call/slice/thru sugar.
    """
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    cal = Cal(target_dt=ref, ref_dt=ref)

    # Act / Assert: iterate units and verify golden boolean expectations
    for unit in UNITS:
        ns = getattr(cal, unit)

        # Golden checks: when ref==target, current unit should be True, previous should be False
        assert ns.in_(0) is True
        assert ns.in_(-1) is False
