"""
Utility tests for helpers and normalization in frist.
"""

import datetime as dt

from frist._util import in_half_open, in_half_open_date, in_half_open_dt


def test_in_half_open_int():
    """
    Test in_half_open for integer boundaries.

    Verifies that values at the start are included, at the end are excluded,
    and values within the half-open interval are included.
    """
    # Arrange & Act & Assert
    assert in_half_open(0, 0, 1) is True  # start included
    assert in_half_open(0, 1, 1) is False  # end excluded
    assert in_half_open(-2, -1, 0) is True  # within interval


def test_in_half_open_dt():
    """
    Test in_half_open_dt for datetime boundaries.

    Checks that the start datetime is included, the end is excluded,
    and values within the interval are included.
    """
    # Arrange
    start = dt.datetime(2025, 1, 1, 0, 0)
    end = dt.datetime(2025, 1, 2, 0, 0)
    # Act & Assert
    assert in_half_open_dt(start, start, end) is True  # start included
    assert in_half_open_dt(start, end, end) is False  # end excluded


def test_in_half_open_date():
    """
    Test in_half_open_date for date boundaries.

    Ensures that the start date is included, the end is excluded,
    and values within the interval are included.
    """
    # Arrange
    start = dt.date(2025, 1, 1)
    end = dt.date(2025, 1, 2)
    # Act & Assert
    assert in_half_open_date(start, start, end) is True  # start included
    assert in_half_open_date(start, end, end) is False  # end excluded
