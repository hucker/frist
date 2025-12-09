"""
Tests for day unit shortcuts and half-open boundary logic in the Cal class.

Verifies that is_today, is_yesterday, and is_tomorrow shortcuts work as expected,
and that day.in_() correctly implements half-open interval boundaries.
"""

import datetime as dt

from frist import Cal


def test_day_unit_shortcuts_today_yesterday_tomorrow():
    """
    Test Cal.day shortcut properties for today, yesterday, and tomorrow.

    Asserts that the is_today, is_yesterday, and is_tomorrow properties
    correctly identify the target date relative to the reference date.
    """
    # Arrange
    ref = dt.datetime(2025, 12, 5, 12, 0)
    # Act & Assert
    # today
    assert Cal(dt.datetime(2025, 12, 5, 9, 0), ref).day.is_today is True
    # yesterday
    assert Cal(dt.datetime(2025, 12, 4, 9, 0), ref).day.is_yesterday is True
    # tomorrow
    assert Cal(dt.datetime(2025, 12, 6, 9, 0), ref).day.is_tomorrow is True


def test_day_unit_in_impl_half_open_boundaries():
    """
    Test Cal.day.in_() method for correct half-open interval boundary behavior.

    Asserts that the [-1, 1) window includes yesterday and today, but excludes
    the exact start of tomorrow.
    """
    # Arrange
    ref = dt.datetime(2025, 12, 5, 0, 0)
    # Act
    cal = Cal(dt.datetime(2025, 12, 5, 23, 59, 59), ref)
    # Assert
    # window [-1, 1) covers yesterday and today (exclusive end at tomorrow)
    assert cal.day.in_(-1, 1) is True
    # Act
    cal2 = Cal(dt.datetime(2025, 12, 6, 0, 0), ref)
    # Assert
    # end exclusive: a time exactly at start of tomorrow is not included
    assert cal2.day.in_(-1, 1) is False