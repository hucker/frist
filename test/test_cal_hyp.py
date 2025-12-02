"""
Property-based tests for the Cal class using Hypothesis.

These tests verify mathematical properties and invariants that should always hold
for Cal calendar window calculations, regardless of input dates.
"""

import datetime as dt
from typing import Tuple

import pytest
from hypothesis import given, strategies as st

from frist import Cal
from frist._cal import normalize_weekday


# Custom strategies for datetime generation
datetime_strategy = st.datetimes(
    min_value=dt.datetime(1900, 1, 1),
    max_value=dt.datetime(2100, 12, 31)
    # Default timezones=st.none() gives naive datetimes only (as per package design)
)

# Strategy for pairs of datetimes where target and reference can be in any order
datetime_pair_strategy = st.tuples(datetime_strategy, datetime_strategy)


@pytest.mark.hypothesis
@given(target_ref=st.tuples(datetime_strategy, datetime_strategy))
def test_cal_construction_properties(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test that Cal objects are constructed correctly."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    assert cal.target_dt == target_dt
    assert cal.ref_dt == ref_dt


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_minutes_consistency(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test in_minutes method consistency."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    # Calculate expected result manually
    time_diff_minutes = (target_dt - ref_dt).total_seconds() / 60

    # Test single minute window
    for offset in range(-10, 11):
        expected = offset <= time_diff_minutes < offset + 1
        assert cal.minute.in_(offset) == expected

    # Test range windows (ensure start < end)
    for start in range(-5, 6):
        for end in range(start + 1, start + 6):
            expected = start <= time_diff_minutes < end
            assert cal.minute.in_(start, end) == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_hours_consistency(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test in_hours method consistency."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    time_diff_hours = (target_dt - ref_dt).total_seconds() / 3600

    # Test single hour window
    for offset in range(-10, 11):
        expected = offset <= time_diff_hours < offset + 1
        assert cal.hour.in_(offset) == expected

    # Test range windows (ensure start < end)
    for start in range(-5, 6):
        for end in range(start + 1, start + 6):
            expected = start <= time_diff_hours < end
            assert cal.hour.in_(start, end) == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_days_consistency(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test in_days method consistency."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    time_diff_days = (target_dt - ref_dt).total_seconds() / 86400

    # Test single day window
    for offset in range(-5, 6):
        expected = offset <= time_diff_days < offset + 1
        assert cal.day.in_(offset) == expected

    # Test range windows (ensure start < end)
    for start in range(-3, 4):
        for end in range(start + 1, start + 4):
            expected = start <= time_diff_days < end
            assert cal.day.in_(start, end) == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_weeks_consistency(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test in_weeks method consistency."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    time_diff_weeks = (target_dt - ref_dt).total_seconds() / (86400 * 7)

    # Test single week window
    for offset in range(-3, 4):
        expected = offset <= time_diff_weeks < offset + 1
        assert cal.week.in_(offset) == expected

    # Test range windows (ensure start < end)
    for start in range(-2, 3):
        for end in range(start + 1, start + 3):
            expected = start <= time_diff_weeks < end
            assert cal.week.in_(start, end) == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_unit_namespace_consistency(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test that UnitNamespace call syntax and thru syntax work correctly."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    # Test call syntax (should delegate to in_)
    assert cal.minute(5, 10) == cal.minute.in_(5, 10)
    assert cal.hour(1, 3) == cal.hour.in_(1, 3)
    assert cal.day(-1, 1) == cal.day.in_(-1, 1)
    assert cal.week(0, 2) == cal.week.in_(0, 2)

    # Test thru syntax (inclusive end)
    assert cal.day.thru(-1, 0) == cal.day.in_(-1, 1)  # -1 through 0 = -1 to 1 (half-open)


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_convenience_methods(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test convenience methods like is_today, is_yesterday, etc."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    # Test is_today (property)
    expected_today = (target_dt.date() == ref_dt.date())
    assert cal.is_today == expected_today

    # Test is_yesterday (property)
    expected_yesterday = (target_dt.date() == ref_dt.date() - dt.timedelta(days=1))
    assert cal.is_yesterday == expected_yesterday

    # Test is_tomorrow (property)
    expected_tomorrow = (target_dt.date() == ref_dt.date() + dt.timedelta(days=1))
    assert cal.is_tomorrow == expected_tomorrow

    # Test is_this_week (property)
    target_week = target_dt.isocalendar()[1]
    ref_week = ref_dt.isocalendar()[1]
    target_year = target_dt.isocalendar()[0]
    ref_year = ref_dt.isocalendar()[0]
    expected_this_week = (target_week == ref_week and target_year == ref_year)
    assert cal.is_this_week == expected_this_week

    # Test is_last_week (property)
    expected_last_week = (target_week == ref_week - 1 and target_year == ref_year) or \
                        (target_week == 52 and ref_week == 1 and target_year == ref_year - 1)
    assert cal.is_last_week == expected_last_week

    # Test is_next_week (property)
    expected_next_week = (target_week == ref_week + 1 and target_year == ref_year) or \
                        (target_week == 1 and ref_week == 52 and target_year == ref_year + 1)
    assert cal.is_next_week == expected_next_week

    # Test is_this_month (property)
    expected_this_month = (target_dt.year == ref_dt.year and target_dt.month == ref_dt.month)
    assert cal.is_this_month == expected_this_month

    # Test is_last_month (property)
    if ref_dt.month == 1:
        expected_last_month = (target_dt.year == ref_dt.year - 1 and target_dt.month == 12)
    else:
        expected_last_month = (target_dt.year == ref_dt.year and target_dt.month == ref_dt.month - 1)
    assert cal.is_last_month == expected_last_month


@pytest.mark.hypothesis
@given(day_spec=st.sampled_from([
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
    'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su',
    'w-mon', 'w-tue', 'w-wed', 'w-thu', 'w-fri', 'w-sat', 'w-sun',
    'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'
]))
def test_normalize_weekday_comprehensive(day_spec: str):
    """Test normalize_weekday function with various inputs."""
    result = normalize_weekday(day_spec)

    # Result should be 0-6 (Monday=0 to Sunday=6)
    assert 0 <= result <= 6

    # Test that equivalent specifications give same result
    lower_spec = day_spec.lower()
    if lower_spec in ['monday', 'mon', 'mo', 'w-mon']:
        assert result == 0
    elif lower_spec in ['tuesday', 'tue', 'tu', 'w-tue']:
        assert result == 1
    elif lower_spec in ['wednesday', 'wed', 'we', 'w-wed']:
        assert result == 2
    elif lower_spec in ['thursday', 'thu', 'th', 'w-thu']:
        assert result == 3
    elif lower_spec in ['friday', 'fri', 'fr', 'w-fri']:
        assert result == 4
    elif lower_spec in ['saturday', 'sat', 'sa', 'w-sat']:
        assert result == 5
    elif lower_spec in ['sunday', 'sun', 'su', 'w-sun']:
        assert result == 6


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_quarter_calculations(target_ref: Tuple[dt.datetime, dt.datetime]):
    """Test quarter-based calculations."""
    target_dt, ref_dt = target_ref
    cal = Cal(target_dt, ref_dt)

    # Calculate quarter difference manually using the same logic as Cal.in_quarters
    base_quarter = ((ref_dt.month - 1) // 3)  # 0..3 offset within year
    base_year = ref_dt.year
    ref_quarter_idx = base_year * 4 + base_quarter

    target_quarter = ((target_dt.month - 1) // 3)
    target_year = target_dt.year
    target_quarter_idx = target_year * 4 + target_quarter

    quarter_diff = target_quarter_idx - ref_quarter_idx

    # Test quarter windows
    for offset in range(-4, 5):
        expected = offset <= quarter_diff < offset + 1
        assert cal.qtr.in_(offset) == expected