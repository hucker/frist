"""
Test file for standalone Cal (calendar) functionality.

Tests the Cal class as a standalone utility for calendar window calculations.
"""

import datetime as dt

import pytest

from frist import Cal, Chrono
from frist._cal import normalize_weekday
from frist._cal_policy import BizPolicy


def test_simple_cal_day_windows():
    """Simple test for Cal: one day apart, check day windows."""
    # Arrange
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    cal: Cal = Cal(target_time, reference_time)
    # Act
    # (no separate action beyond construction)

    # Assert
    assert cal.target_dt == target_time, "cal.target_dt should match target_time"
    assert cal.ref_dt == reference_time, "cal.ref_dt should match reference_time"
    assert cal.in_days(-1, 0), "Target should be yesterday relative to reference"
    assert cal.in_days(-1, 0), "Target should be in range yesterday through today"
    assert not cal.in_days(0), "Target should not be today"
    assert not cal.in_days(-2), "Target should not be two days ago"


def test_cal_with_chrono():
    """Test Cal functionality using Chrono objects."""
    """
The file was created successfully. The tool showed some lint suggestions when creating files, which is expected for tests (type errors from intentional wrong-type calls). Now I'll run tests with the venv Python to get the coverage report. I'll run pytest using the project's virtualenv python executable. Please hold on for the test run output.