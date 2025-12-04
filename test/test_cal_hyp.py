"""
Property-based tests for the Cal class using Hypothesis.

These tests verify mathematical properties and invariants that should always hold
for Cal calendar window calculations, regardless of input dates.
"""

import datetime as dt

import pytest
from hypothesis import given
from hypothesis import strategies as st

from frist._cal import Cal
from frist._util import normalize_weekday

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
def test_cal_construction_properties(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test that Cal objects are constructed correctly."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    # Assert
    expected_target = target_dt
    expected_ref = ref_dt
    actual_target = cal.target_dt
    actual_ref = cal.ref_dt
    assert actual_target == expected_target
    assert actual_ref == expected_ref


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_minutes_consistency(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test in_minutes method consistency."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    time_diff_minutes = (target_dt - ref_dt).total_seconds() / 60
    # Assert
    for offset in range(-10, 11):
        expected = offset <= time_diff_minutes < offset + 1
        actual = cal.minute.in_(offset)
        assert actual == expected
    for start in range(-5, 6):
        for end in range(start + 1, start + 6):
            expected = start <= time_diff_minutes < end
            actual = cal.minute.in_(start, end)
            assert actual == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_hours_consistency(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test in_hours method consistency."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    time_diff_hours = (target_dt - ref_dt).total_seconds() / 3600
    # Assert
    for offset in range(-10, 11):
        expected = offset <= time_diff_hours < offset + 1
        actual = cal.hour.in_(offset)
        assert actual == expected
    for start in range(-5, 6):
        for end in range(start + 1, start + 6):
            expected = start <= time_diff_hours < end
            actual = cal.hour.in_(start, end)
            assert actual == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_days_consistency(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test in_days method consistency."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    time_diff_days = (target_dt - ref_dt).total_seconds() / 86400
    # Assert
    for offset in range(-5, 6):
        expected = offset <= time_diff_days < offset + 1
        actual = cal.day.in_(offset)
        assert actual == expected
    for start in range(-3, 4):
        for end in range(start + 1, start + 4):
            expected = start <= time_diff_days < end
            actual = cal.day.in_(start, end)
            assert actual == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_in_weeks_consistency(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test in_weeks method consistency."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    week_start_day = normalize_weekday("monday")
    target_date = target_dt.date()
    base_date = ref_dt.date()
    days_since_week_start = (base_date.weekday() - week_start_day) % 7
    current_week_start = base_date - dt.timedelta(days=days_since_week_start)
    week_offset = (target_date - current_week_start).days // 7
    # Assert
    for offset in range(-3, 4):
        expected = (week_offset == offset)
        actual = cal.week.in_(offset)
        assert actual == expected
    for start in range(-2, 3):
        for end in range(start + 1, start + 3):
            expected = (start <= week_offset < end)
            actual = cal.week.in_(start, end)
            assert actual == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_unit_namespace_consistency(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test that UnitNamespace call syntax and thru syntax work correctly."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    # Assert
    expected_minute = cal.minute.in_(5, 10)
    actual_minute = cal.minute(5, 10)
    assert actual_minute == expected_minute
    expected_hour = cal.hour.in_(1, 3)
    actual_hour = cal.hour(1, 3)
    assert actual_hour == expected_hour
    expected_day = cal.day.in_(-1, 1)
    actual_day = cal.day(-1, 1)
    assert actual_day == expected_day
    expected_week = cal.week.in_(0, 2)
    actual_week = cal.week(0, 2)
    assert actual_week == expected_week
    expected_thru = cal.day.in_(-1, 1)
    actual_thru = cal.day.thru(-1, 0)
    assert actual_thru == expected_thru  # -1 through 0 = -1 to 1 (half-open)


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_convenience_methods(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test convenience methods like is_today, is_yesterday, etc."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    # Assert
    expected_today = (target_dt.date() == ref_dt.date())
    actual_today = cal.is_today
    assert actual_today == expected_today
    expected_yesterday = (target_dt.date() == ref_dt.date() - dt.timedelta(days=1))
    actual_yesterday = cal.is_yesterday
    assert actual_yesterday == expected_yesterday
    expected_tomorrow = (target_dt.date() == ref_dt.date() + dt.timedelta(days=1))
    actual_tomorrow = cal.is_tomorrow
    assert actual_tomorrow == expected_tomorrow
    target_week = target_dt.isocalendar()[1]
    ref_week = ref_dt.isocalendar()[1]
    target_year = target_dt.isocalendar()[0]
    ref_year = ref_dt.isocalendar()[0]
    expected_this_week = (target_week == ref_week and target_year == ref_year)
    actual_this_week = cal.is_this_week
    assert actual_this_week == expected_this_week
    expected_last_week = (
        (target_week == ref_week - 1 and target_year == ref_year) or
        (target_week == 52 and ref_week == 1 and target_year == ref_year - 1)
    )
    actual_last_week = cal.is_last_week
    assert actual_last_week == expected_last_week
    expected_next_week = (
        (target_week == ref_week + 1 and target_year == ref_year) or
        (target_week == 1 and ref_week == 52 and target_year == ref_year + 1)
    )
    actual_next_week = cal.is_next_week
    assert actual_next_week == expected_next_week
    expected_this_month = (
        target_dt.year == ref_dt.year and target_dt.month == ref_dt.month
    )
    actual_this_month = cal.is_this_month
    assert actual_this_month == expected_this_month
    if ref_dt.month == 1:
        expected_last_month = (
            target_dt.year == ref_dt.year - 1 and target_dt.month == 12
        )
    else:
        expected_last_month = (
            target_dt.year == ref_dt.year and target_dt.month == ref_dt.month - 1
        )
    actual_last_month = cal.is_last_month
    assert actual_last_month == expected_last_month


@pytest.mark.hypothesis
@given(day_spec=st.sampled_from([
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "mon", "tue", "wed", "thu", "fri", "sat", "sun",
    "mo", "tu", "we", "th", "fr", "sa", "su",
    "w-mon", "w-tue", "w-wed", "w-thu", "w-fri", "w-sat", "w-sun",
    "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"
]))
def test_normalize_weekday_comprehensive(day_spec: str):
    """Test normalize_weekday function with various inputs."""
    # Arrange & Act
    actual = normalize_weekday(day_spec)
    # Assert
    assert 0 <= actual <= 6
    lower_spec = day_spec.lower()
    if lower_spec in ["monday", "mon", "mo", "w-mon"]:
        expected = 0
    elif lower_spec in ["tuesday", "tue", "tu", "w-tue"]:
        expected = 1
    elif lower_spec in ["wednesday", "wed", "we", "w-wed"]:
        expected = 2
    elif lower_spec in ["thursday", "thu", "th", "w-thu"]:
        expected = 3
    elif lower_spec in ["friday", "fri", "fr", "w-fri"]:
        expected = 4
    elif lower_spec in ["saturday", "sat", "sa", "w-sat"]:
        expected = 5
    elif lower_spec in ["sunday", "sun", "su", "w-sun"]:
        expected = 6
    else:
        expected = actual
    assert actual == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy)
def test_cal_quarter_calculations(target_ref: tuple[dt.datetime, dt.datetime]):
    """Test quarter-based calculations."""
    # Arrange
    target_dt, ref_dt = target_ref
    # Act
    cal = Cal(target_dt, ref_dt)
    base_quarter = ((ref_dt.month - 1) // 3)
    base_year = ref_dt.year
    ref_quarter_idx = base_year * 4 + base_quarter
    target_quarter = ((target_dt.month - 1) // 3)
    target_year = target_dt.year
    target_quarter_idx = target_year * 4 + target_quarter
    quarter_diff = target_quarter_idx - ref_quarter_idx
    # Assert
    for offset in range(-4, 5):
        expected = offset <= quarter_diff < offset + 1
        actual = cal.qtr.in_(offset)
        assert actual == expected