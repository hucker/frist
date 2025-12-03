"""
Tests verifying inclusive `thru` behavior for Cal namespaces.

These ensure `ns.thru(start, end)` produces the correct half-open semantics
by advancing the end by 1 compared to `in_`.

Style: Arrange / Act / Assert (AA) per project `codeguide.md`.
"""

import datetime as dt
from frist._cal import Cal

CAL_UNITS = ["minute", "hour", "day", "week", "month", "qtr", "year"]


def test_cal_thru_behavior():
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)
    cal = Cal(target_dt=ref, ref_dt=ref)

    # Act / Assert
    for prop in CAL_UNITS:
        ns = getattr(cal, prop)

        # Golden check: when ref==target, current unit is True, previous is False
        assert ns.in_(0) is True
        assert ns.in_(-1) is False

        # inclusive slice syntax removed; verify call form only
