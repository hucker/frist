"""
Test file for standalone Zeit functionality.

Tests the Zeit class as a standalone dt.datetime utility without file dependencies.
"""

import datetime as dt

import pytest

from frist import Chrono


def test_chrono_creation():
    """Test basic Chrono object creation."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    # Test with explicit reference time
    z = Chrono(target_time=target_time, reference_time=reference_time)
    assert z.target_time == target_time
    assert z.reference_time == reference_time

    # Test with default reference time (now)
    zeit_now = Chrono(target_time=target_time)

    assert zeit_now.target_time == target_time
    assert zeit_now.reference_time is not None


def test_chrono_properties():
    """Test Chrono object properties."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    z = Chrono(target_time=target_time, reference_time=reference_time)

    # Test basic properties
    assert z.timestamp == target_time.timestamp()



def test_chrono_age_property():
    """Test that Chrono age property works correctly."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    z = Chrono(target_time=target_time, reference_time=reference_time)
    age = z.age

    # Test that age calculations work
    assert age.seconds == 86400.0
    assert age.minutes == 1440.0
    assert age.hours == 24.0
    assert age.days == 1.0
    assert age.weeks == pytest.approx(1.0 / 7.0) # type: ignore


def test_chrono_calendar_property():
    """Test that Chrono calendar property works correctly."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 1, 18, 0, 0)  # Same day, 6 hours later

    z = Chrono(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test calendar window functionality
    assert cal.in_days(0)  # Same day
    assert cal.in_hours(-6, 0)  # Within 6 hours
    assert not cal.in_days(-1)  # Not yesterday


def test_chrono_with_reference_time():
    """Test creating new Chrono with different reference time."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    original_ref = dt.datetime(2024, 1, 2, 12, 0, 0)
    new_ref = dt.datetime(2024, 1, 3, 12, 0, 0)

    zeit1 = Chrono(target_time=target_time, reference_time=original_ref)
    zeit2 = zeit1.with_reference_time(new_ref)

    # Original should be unchanged
    assert zeit1.reference_time == original_ref

    # New one should have different reference
    assert zeit2.reference_time == new_ref
    assert zeit2.target_time == target_time  # Same target


def test_chrono_string_representations():
    """Test string representations of Chrono objects."""
    target_time = dt.datetime(2024, 1, 1, 12, 30, 45)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    z = Chrono(target_time=target_time, reference_time=reference_time)

    # Test __repr__
    repr_str = repr(z)
    assert "Chrono" in repr_str
    assert "2024-01-01T12:30:45" in repr_str
    assert "2024-01-02T12:00:00" in repr_str

    # Test __str__
    str_str = str(z)
    assert "Chrono for 2024-01-01 12:30:45" in str_str


def test_chrono_parse_static_method():
    """Test Chrono.parse static method."""
    # Test Unix timestamp
    zeit1 = Chrono.parse("1704110400")  # 2024-01-01 12:00:00 UTC
    assert zeit1.target_time.year == 2024
    assert zeit1.target_time.month == 1
    assert zeit1.target_time.day == 1

    # Test ISO format
    zeit2 = Chrono.parse("2024-01-01T12:30:00")
    assert zeit2.target_time.hour == 12
    assert zeit2.target_time.minute == 30

    # Test simple date
    zeit3 = Chrono.parse("2024-12-25")
    assert zeit3.target_time.month == 12
    assert zeit3.target_time.day == 25

    # Test with custom reference time
    ref_time = dt.datetime(2024, 6, 1)
    zeit4 = Chrono.parse("2024-01-01", ref_time)
    assert zeit4.reference_time == ref_time


def test_chrono_parse_errors():
    """Test Chrono.parse error handling."""
    with pytest.raises(ValueError, match="Unable to parse time string"):
        Chrono.parse("invalid-date-format")

    with pytest.raises(ValueError, match="Unable to parse time string"):
        Chrono.parse("not-a-date-at-all")


def test_chrono_fiscal_properties():
    """Test fiscal year and quarter properties."""
    # Default fiscal year (starts in January)
    target_time = dt.datetime(2024, 2, 15)
    z = Chrono(target_time=target_time)
    assert z.cal.fiscal_year == 2024
    assert z.cal.fiscal_quarter == 1  # Jan-Mar

    # Fiscal year starting in April
    zeit_april = Chrono(target_time=target_time, fy_start_month=4)
    assert zeit_april.cal.fiscal_year == 2023  # Feb is before April start
    assert zeit_april.cal.fiscal_quarter == 4  # Jan-Mar is Q4 for April start

    target_time_july = dt.datetime(2024, 7, 15)
    zeit_july = Chrono(target_time=target_time_july, fy_start_month=4)
    assert zeit_july.cal.fiscal_year == 2024
    assert zeit_july.cal.fiscal_quarter == 2  # Jul-Sep is Q2 for April start


def test_chrono_holiday_property():
    """Test holiday detection property."""
    holidays = {'2024-01-01', '2024-12-25'}
    target_time = dt.datetime(2024, 1, 1)
    z = Chrono(target_time=target_time, holidays=holidays)
    assert z.cal.holiday is True

    target_time_not_holiday = dt.datetime(2024, 7, 4)
    zeit_not = Chrono(target_time=target_time_not_holiday, holidays=holidays)
    assert zeit_not.cal.holiday is False

    # Empty holidays
    zeit_empty = Chrono(target_time=target_time, holidays=set())
    assert zeit_empty.cal.holiday is False


