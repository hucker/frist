"""
Explicit membership checks for compact units using `Cal`.

Follows CODESTYLE with AAA comments and direct Act/Assert for simple cases.
"""

import datetime as dt

from frist._cal import Cal


def test_unit_explicit_checks():
    """Explicit checks for each compact unit against a concrete Cal.

    Uses a reference datetime and a target equal to the reference so the
    expected membership is straightforward: the 0 offset should be True and
    negative offsets should be False for each unit.
    """
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 34, 56)  # Saturday, 2025-03-15
    cal = Cal(target_dt=ref, ref_dt=ref)

    # Act / Assert: Minutes
    assert cal.minute.in_(0) is True
    assert cal.minute.in_(-1) is False

    # Act / Assert: Hours
    assert cal.hour.in_(0) is True
    assert cal.hour.in_(1) is False

    # Act / Assert: Days
    assert cal.day.in_(0) is True
    assert cal.day.in_(-1) is False

    # Act / Assert: Weeks (ISO Monday start)
    assert cal.week.in_(0) is True
    assert cal.week.in_(-1) is False

    # Act / Assert: Months
    assert cal.month.in_(0) is True
    assert cal.month.in_(-1) is False

    # Act / Assert: Quarters
    assert cal.qtr.in_(0) is True
    assert cal.qtr.in_(-1) is False

    # Act / Assert: Years
    assert cal.year.in_(0) is True
    assert cal.year.in_(-1) is False
