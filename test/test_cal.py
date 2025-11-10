"""
Test file for standalone Cal (calendar) functionality.

Tests the Cal class as a standalone utility for calendar window calculations.
"""

import datetime as dt

import pytest

from frist import Cal, Frist
from frist._cal import normalize_weekday


def test_cal_with_zeit():
    """Test Cal functionality using Frist objects."""
    # Create a Frist object for January 1, 2024 at noon
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 1, 18, 0, 0)  # Same day, 6 hours later

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test that we can access calendar functionality
    assert isinstance(cal, Cal)
    assert cal.dt_val == target_time
    assert cal.base_time == reference_time


def test_cal_in_minutes():
    """Test calendar minute window functionality."""
    target_time = dt.datetime(2024, 1, 1, 12, 30, 0)
    reference_time = dt.datetime(2024, 1, 1, 12, 35, 0)  # 5 minutes later

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be within current minute range
    assert cal.in_minutes(-5, 0)  # Last 5 minutes through now
    assert not cal.in_minutes(1, 5)  # Future minutes
    assert cal.in_minutes(-10, 0)  # Broader range including target


def test_cal_in_hours():
    """Test calendar hour window functionality."""
    target_time = dt.datetime(2024, 1, 1, 10, 30, 0)
    reference_time = dt.datetime(2024, 1, 1, 12, 30, 0)  # 2 hours later

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be within hour ranges
    assert cal.in_hours(-2, 0)  # Last 2 hours through now
    assert not cal.in_hours(-1, 0)  # Just last hour (too narrow)
    assert cal.in_hours(-3, 0)  # Broader range


def test_cal_in_days():
    """Test calendar day window functionality."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)  # Next day

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test day windows
    assert cal.in_days(-1, 0)  # Yesterday through today
    assert cal.in_days(-1)  # Just yesterday
    assert not cal.in_days(0)  # Just today (target was yesterday)
    assert not cal.in_days(-2, -2)  # Two days ago only


def test_cal_in_weeks():
    """Test calendar week window functionality."""
    # Monday Jan 1, 2024
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)  # Monday
    reference_time = dt.datetime(2024, 1, 8, 12, 0, 0)  # Next Monday

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test week windows
    assert cal.in_weeks(-1, 0)  # Last week through this week
    assert cal.in_weeks(-1)  # Just last week
    assert not cal.in_weeks(0)  # Just this week


def test_cal_in_weeks_custom_start():
    """Test calendar week functionality with custom week start."""
    # Sunday Jan 7, 2024
    target_time = dt.datetime(2024, 1, 7, 12, 0, 0)  # Sunday
    reference_time = dt.datetime(2024, 1, 14, 12, 0, 0)  # Next Sunday

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test with Sunday week start
    assert cal.in_weeks(-1, week_start="sunday")
    assert cal.in_weeks(-1, week_start="sun")
    assert cal.in_weeks(-1, week_start="su")


def test_cal_in_months():
    """Test calendar month window functionality."""
    target_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 15
    reference_time = dt.datetime(2024, 2, 15, 12, 0, 0)  # February 15

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test month windows
    assert cal.in_months(-1, 0)  # Last month through this month
    assert cal.in_months(-1)  # Just last month
    assert not cal.in_months(0)  # Just this month


def test_cal_in_quarters():
    """Test calendar quarter window functionality."""
    target_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1 2024
    reference_time = dt.datetime(2024, 4, 15, 12, 0, 0)  # Q2 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test quarter windows
    assert cal.in_quarters(-1, 0)  # Last quarter through this quarter
    assert cal.in_quarters(-1)  # Just last quarter (Q1)
    assert not cal.in_quarters(0)  # Just this quarter (Q2)


def test_cal_in_years():
    """Test calendar year window functionality."""
    target_time = dt.datetime(2023, 6, 15, 12, 0, 0)  # 2023
    reference_time = dt.datetime(2024, 6, 15, 12, 0, 0)  # 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test year windows
    assert cal.in_years(-1, 0)  # Last year through this year
    assert cal.in_years(-1)  # Just last year
    assert not cal.in_years(0)  # Just this year




def test_cal_single_vs_range():
    """Test single time unit vs range specifications."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Single day (yesterday only)
    assert cal.in_days(-1)  # Just yesterday

    # Range (yesterday through today)
    assert cal.in_days(-1, 0)  # Yesterday through today


def test_weekday_normalization():
    """Test the normalize_weekday function indirectly through Cal."""
    # Test full names
    assert normalize_weekday("monday") == 0
    assert normalize_weekday("sunday") == 6

    # Test 3-letter abbreviations
    assert normalize_weekday("mon") == 0
    assert normalize_weekday("sun") == 6

    # Test 2-letter abbreviations
    assert normalize_weekday("mo") == 0
    assert normalize_weekday("su") == 6

    # Test case insensitivity
    assert normalize_weekday("MONDAY") == 0
    assert normalize_weekday("Sun") == 6

    # Test pandas style
    assert normalize_weekday("w-mon") == 0
    assert normalize_weekday("w-sun") == 6


def test_weekday_normalization_errors():
    """Test error handling in weekday normalization."""
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("invalid")

    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("xyz")


def test_cal_edge_cases():
    """Test edge cases in calendar functionality."""
    # Test with same date/time (zero difference)
    target_time = dt.datetime(2024, 1, 15, 12, 30, 0)
    reference_time = dt.datetime(2024, 1, 15, 12, 30, 0)

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # All current windows should return True
    assert cal.in_minutes(0)
    assert cal.in_hours(0)
    assert cal.in_days(0)
    assert cal.in_months(0)
    assert cal.in_quarters(0)
    assert cal.in_years(0)
    assert cal.in_weeks(0)


def test_cal_month_edge_cases():
    """Test month calculations across year boundaries."""
    # Test December to January transition
    target_time = dt.datetime(2023, 12, 15, 12, 0, 0)  # December 2023
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be in the previous month
    assert cal.in_months(-1)  # Last month
    assert not cal.in_months(0)  # This month

    # Test multiple years back
    target_time = dt.datetime(2022, 6, 15, 12, 0, 0)  # June 2022
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be about 19 months ago
    assert cal.in_months(-20, -18)
    assert not cal.in_months(-12, 0)


def test_cal_quarter_edge_cases():
    """Test quarter calculations across year boundaries."""
    # Q4 2023 to Q1 2024 transition
    target_time = dt.datetime(2023, 11, 15, 12, 0, 0)  # Q4 2023
    reference_time = dt.datetime(2024, 2, 15, 12, 0, 0)  # Q1 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be in the previous quarter
    assert cal.in_quarters(-1)  # Last quarter
    assert not cal.in_quarters(0)  # This quarter

    # Test edge quarters
    target_time = dt.datetime(2024, 3, 31, 12, 0, 0)  # End of Q1
    reference_time = dt.datetime(2024, 4, 1, 12, 0, 0)  # Start of Q2

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    assert cal.in_quarters(-1)  # Previous quarter
    assert not cal.in_quarters(0)  # Current quarter


def test_cal_year_edge_cases():
    """Test year calculations."""
    # Year boundary test
    target_time = dt.datetime(2023, 12, 31, 23, 59, 59)  # End of 2023
    reference_time = dt.datetime(2024, 1, 1, 0, 0, 1)  # Start of 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be in the previous year
    assert cal.in_years(-1)  # Last year
    assert not cal.in_years(0)  # This year

    # Multi-year range
    assert cal.in_years(-2, 0)  # 2 years ago through now


def test_cal_week_different_starts():
    """Test week calculations with different start days."""
    # Test with a clear week boundary
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)  # Monday, Jan 1
    reference_time = dt.datetime(2024, 1, 8, 12, 0, 0)  # Monday, Jan 8 (next week)

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # With Monday start, target should be exactly one week ago
    assert cal.in_weeks(-1, week_start='monday')
    assert not cal.in_weeks(0, week_start='monday')

    # Test Sunday start with different dates to avoid edge cases
    target_time = dt.datetime(2024, 1, 7, 12, 0, 0)  # Sunday
    reference_time = dt.datetime(2024, 1, 14, 12, 0, 0)  # Next Sunday

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test Sunday-based weeks
    assert cal.in_weeks(-1, week_start='sunday')


def test_cal_minutes_edge_cases():
    """Test minute window edge cases."""
    # Test minute boundaries
    target_time = dt.datetime(2024, 1, 1, 12, 29, 59)  # End of minute 29
    reference_time = dt.datetime(2024, 1, 1, 12, 30, 0)  # Start of minute 30

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be in the previous minute
    assert cal.in_minutes(-1)  # Previous minute
    assert not cal.in_minutes(0)  # Current minute

    # Test range spanning multiple minutes
    assert cal.in_minutes(-5, 0)  # 5 minutes ago through now


def test_cal_hours_edge_cases():
    """Test hour window edge cases."""
    # Test hour boundaries
    target_time = dt.datetime(2024, 1, 1, 11, 59, 59)  # End of hour 11
    reference_time = dt.datetime(2024, 1, 1, 12, 0, 0)  # Start of hour 12

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Should be in the previous hour
    assert cal.in_hours(-1)  # Previous hour
    assert not cal.in_hours(0)  # Current hour

    # Test range spanning multiple hours
    assert cal.in_hours(-6, 0)  # 6 hours ago through now


def test_cal_future_windows():
    """Test calendar windows for future dates."""
    # Target is in the future
    target_time = dt.datetime(2024, 1, 2, 12, 0, 0)  # Tomorrow
    reference_time = dt.datetime(2024, 1, 1, 12, 0, 0)  # Today

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test future windows
    assert cal.in_days(1)  # Tomorrow
    assert cal.in_hours(24)  # 24 hours from now
    assert cal.in_minutes(1440)  # 1440 minutes from now

    # Future weeks
    assert cal.in_weeks(0, 1)  # This week through next week

    # Future months
    target_time = dt.datetime(2024, 2, 15, 12, 0, 0)  # Next month
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # This month

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    assert cal.in_months(1)  # Next month

    # Future quarters
    target_time = dt.datetime(2024, 7, 15, 12, 0, 0)  # Q3
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    assert cal.in_quarters(2)  # 2 quarters from now

    # Future years
    target_time = dt.datetime(2026, 1, 15, 12, 0, 0)  # 2026
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    assert cal.in_years(2)  # 2 years from now


def test_cal_month_complex_calculations():
    """Test complex month calculations that cross multiple year boundaries."""
    # Test going back many months across years
    target_time = dt.datetime(2021, 3, 15, 12, 0, 0)  # March 2021
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Calculate exact months back: from March 2021 to January 2024
    # From March 2021 to January 2022 = 10 months
    # From January 2022 to January 2024 = 24 months
    # Total = 34 months back
    assert cal.in_months(-34)  # Exactly 34 months ago
    assert cal.in_months(-35, -33)  # Range around the target


def test_cal_quarter_complex_calculations():
    """Test complex quarter calculations across multiple years."""
    # Test going back many quarters
    target_time = dt.datetime(2021, 7, 15, 12, 0, 0)  # Q3 2021
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # This should be about 10 quarters ago
    assert cal.in_quarters(-12, -8)  # Allow some range


def test_normalize_weekday_comprehensive():
    """Test all normalize_weekday formats comprehensively."""
    # Test Tuesday in all formats
    assert normalize_weekday("tuesday") == 1
    assert normalize_weekday("TUESDAY") == 1
    assert normalize_weekday("tue") == 1
    assert normalize_weekday("TUE") == 1
    assert normalize_weekday("tu") == 1
    assert normalize_weekday("TU") == 1
    assert normalize_weekday("w-tue") == 1
    assert normalize_weekday("W-TUE") == 1

    # Test Wednesday in all formats
    assert normalize_weekday("wednesday") == 2
    assert normalize_weekday("wed") == 2
    assert normalize_weekday("we") == 2
    assert normalize_weekday("w-wed") == 2

    # Test Thursday in all formats
    assert normalize_weekday("thursday") == 3
    assert normalize_weekday("thu") == 3
    assert normalize_weekday("th") == 3
    assert normalize_weekday("w-thu") == 3

    # Test Friday in all formats
    assert normalize_weekday("friday") == 4
    assert normalize_weekday("fri") == 4
    assert normalize_weekday("fr") == 4
    assert normalize_weekday("w-fri") == 4

    # Test Saturday in all formats
    assert normalize_weekday("saturday") == 5
    assert normalize_weekday("sat") == 5
    assert normalize_weekday("sa") == 5
    assert normalize_weekday("w-sat") == 5


def test_cal_properties():
    """Test Cal object properties."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # Test that properties return correct values
    assert cal.dt_val == target_time
    assert cal.base_time == reference_time
    assert cal.time_span == z




def test_cal_month_year_rollover_edge_cases():
    """Test month calculations with complex year rollovers."""
    # Test cases that exercise the while loops in month calculations

    # Case 1: Many months in the past that requires multiple year adjustments
    target_time = dt.datetime(2020, 1, 15, 12, 0, 0)
    reference_time = dt.datetime(2024, 12, 15, 12, 0, 0)

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # This should be about 59 months ago
    assert cal.in_months(-60, -58)

    # Case 2: Many months in the future
    target_time = dt.datetime(2028, 12, 15, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 15, 12, 0, 0)

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # This should be about 59 months in the future
    assert cal.in_months(58, 60)


def test_cal_quarter_year_rollover_edge_cases():
    """Test quarter calculations with complex year rollovers."""
    # Test cases that exercise the while loops in quarter calculations

    # Case 1: Many quarters in the past
    target_time = dt.datetime(2020, 2, 15, 12, 0, 0)  # Q1 2020
    reference_time = dt.datetime(2024, 11, 15, 12, 0, 0)  # Q4 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # This should be about 19 quarters ago
    assert cal.in_quarters(-20, -18)

    # Case 2: Many quarters in the future
    target_time = dt.datetime(2029, 8, 15, 12, 0, 0)  # Q3 2029
    reference_time = dt.datetime(2024, 2, 15, 12, 0, 0)  # Q1 2024

    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    # This should be about 22 quarters in the future
    assert cal.in_quarters(21, 23)


def test_normalize_weekday_error_with_detailed_message():
    """Test that normalize_weekday provides helpful error messages."""
    with pytest.raises(ValueError) as excinfo:
        normalize_weekday("invalid_day")
    error_msg = str(excinfo.value)
    # Check that the error message contains helpful examples
    assert "Invalid day specification" in error_msg
    assert "Full:" in error_msg
    assert "3-letter:" in error_msg
    assert "2-letter:" in error_msg
    assert "Pandas:" in error_msg


def test_cal_direct_instantiation():
    """Test creating Cal object directly with a TimeSpan-like object."""
    # Create a simple TimeSpan-like object
    class SimpleTimeSpan:
        def __init__(self, target_dt, ref_dt):
            self._target_dt = target_dt
            self._ref_dt = ref_dt

        @property
        def target_dt(self):
            return self._target_dt

        @property
        def ref_dt(self):
            return self._ref_dt

    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    time_span = SimpleTimeSpan(target_time, reference_time)
    cal = Cal(time_span)

    # Test basic functionality
    assert cal.dt_val == target_time
    assert cal.base_time == reference_time
    assert cal.time_span == time_span
    assert cal.in_days(-1)  # Yesterday


def test_cal_type_checking_imports():
    """Test that TYPE_CHECKING imports work correctly."""
    # Import the module to ensure TYPE_CHECKING code paths are exercised
    import frist._cal as cal_module

    # Check that the module has the expected attributes
    assert hasattr(cal_module, 'Cal')
    assert hasattr(cal_module, 'TimeSpan')
    assert hasattr(cal_module, 'normalize_weekday')

    # Verify TYPE_CHECKING behavior by checking typing imports exist
    assert hasattr(cal_module, 'TYPE_CHECKING')

    # Test that we can instantiate and use the classes
    from typing import TYPE_CHECKING
    assert TYPE_CHECKING is False  # Should be False at runtime



def test_in_xxx_raises_on_backwards_ranges():
    target_time = dt.datetime(2024, 6, 15, 12, 0, 0)
    reference_time = dt.datetime(2024, 6, 15, 12, 0, 0)
    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal

    with pytest.raises(ValueError):
        cal.in_days(2, -2)
    with pytest.raises(ValueError):
        cal.in_months(5, 0)
    with pytest.raises(ValueError):
        cal.in_quarters(3, 1)
    with pytest.raises(ValueError):
        cal.in_years(4, 2)
    with pytest.raises(ValueError):
        cal.in_weeks(3, 0)
    with pytest.raises(ValueError):
        cal.in_hours(10, 5)
    with pytest.raises(ValueError):
        cal.in_minutes(15, 10)


def test_fiscal_year_and_quarter_january_start():
    """Fiscal year and quarter with January start (default)."""
    target_time = dt.datetime(2024, 2, 15)  # February 2024
    z = Frist(target_time=target_time)
    cal = z.cal
    assert z.cal.fiscal_year == 2024
    assert cal.fiscal_year == 2024
    assert z.cal.fiscal_quarter == 1  # Jan-Mar
    assert cal.fiscal_quarter == 1

    target_time = dt.datetime(2024, 4, 1)  # April 2024
    z = Frist(target_time=target_time)
    cal = z.cal
    assert z.cal.fiscal_quarter == 2  # Apr-Jun
    assert cal.fiscal_quarter == 2


def test_fiscal_year_and_quarter_april_start():
    """Fiscal year and quarter with April start."""
    target_time = dt.datetime(2024, 3, 31)  # March 2024
    z = Frist(target_time=target_time, fy_start_month=4)
    cal = z.cal
    assert z.cal.fiscal_year == 2023  # Fiscal year starts in April
    assert cal.fiscal_year == 2023
    assert z.cal.fiscal_quarter == 4  # Jan-Mar is Q4 for April start
    assert cal.fiscal_quarter == 4

    target_time = dt.datetime(2024, 4, 1)  # April 2024
    z = Frist(target_time=target_time, fy_start_month=4)
    cal = z.cal
    assert z.cal.fiscal_year == 2024
    assert cal.fiscal_year == 2024
    assert z.cal.fiscal_quarter == 1  # Apr-Jun is Q1 for April start
    assert cal.fiscal_quarter == 1

    target_time = dt.datetime(2024, 7, 15)  # July 2024
    z = Frist(target_time=target_time, fy_start_month=4)
    cal = z.cal
    assert z.cal.fiscal_quarter == 2  # Jul-Sep is Q2 for April start
    assert cal.fiscal_quarter == 2

    target_time = dt.datetime(2024, 10, 1)  # October 2024
    z = Frist(target_time=target_time, fy_start_month=4)
    cal = z.cal
    assert z.cal.fiscal_quarter == 3  # Oct-Dec is Q3 for April start
    assert cal.fiscal_quarter == 3

    target_time = dt.datetime(2025, 1, 1)  # January 2025
    z = Frist(target_time=target_time, fy_start_month=4)
    cal = z.cal
    assert z.cal.fiscal_quarter == 4  # Jan-Mar is Q4 for April start
    assert cal.fiscal_quarter == 4
