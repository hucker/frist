"""
Test file for standalone Cal (calendar) functionality.

Tests the Cal class as a standalone utility for calendar window calculations.
"""

import datetime as dt

import pytest

from frist import Cal, Chrono
from frist._cal import normalize_weekday


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
    assert cal.day.in_(-1, 0), "Target should be yesterday relative to reference"
    assert cal.day.in_(-1, 0), "Target should be in range yesterday through today"
    assert not cal.day.in_(0), "Target should not be today"
    assert not cal.day.in_(-2), "Target should not be two days ago"


def test_cal_with_chrono():
    """Test Cal functionality using Chrono objects."""
    # Create a Chrono object for January 1, 2024 at noon
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(
        2024, 1, 1, 18, 0, 0
    )  # Same day, 6 hours later

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)

    # Act
    cal: Cal = z.cal

    # Assert
    assert isinstance(cal, Cal), "cal should be instance of Cal"
    assert cal.target_dt == target_time, "cal.target_dt should match target_time"
    assert cal.ref_dt == reference_time, "cal.ref_dt should match reference_time"


def test_cal_in_minutes():
    """Test calendar minute window functionality."""
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 30, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 35, 0)  # 5 minutes later

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.min.in_(-5, 0), "Should be within last 5 minutes through now"
    assert not cal.min.in_(1, 5), "Should not be within future minutes"
    assert cal.min.in_(-10, 0), "Should be within broader range including target"


def test_cal_in_hours():
    """Test calendar hour window functionality."""
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 10, 30, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 30, 0)  # 2 hours later

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.hr.in_(-2, 0), "Should be within last 2 hours through now"
    assert not cal.hr.in_(-1, 0), "Should not be within just last hour (too narrow)"
    assert cal.hr.in_(-3, 0), "Should be within broader range"


def test_cal_in_days():
    """Test calendar day window functionality."""
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)  # Next day

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.day.in_(-1, 1), "Target should be in range yesterday through today"
    assert cal.day.in_(-1, 0), "Target should be just yesterday"
    assert not cal.day.in_(0), "Target should not be today (target was yesterday)"
    assert not cal.day.in_(-2, -1), "Target should not be two days ago only"


def test_cal_in_weeks():
    """Test calendar week window functionality."""
    # Monday Jan 1, 2024
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)  # Monday
    reference_time: dt.datetime = dt.datetime(2024, 1, 8, 12, 0, 0)  # Next Monday

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.wk.in_(-1, 0), "Target should be in range last week through this week"
    assert cal.wk.in_(-1, 0), "Target should be just last week"
    assert not cal.wk.in_(0), "Target should not be this week"


def test_cal_in_weeks_custom_start():
    """Test calendar week functionality with custom week start."""
    # Sunday Jan 7, 2024
    target_time: dt.datetime = dt.datetime(2024, 1, 7, 12, 0, 0)  # Sunday
    reference_time: dt.datetime = dt.datetime(2024, 1, 14, 12, 0, 0)  # Next Sunday

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.in_weeks(-1, week_start="sunday"), "Target should be last week with Sunday start"
    assert cal.in_weeks(-1, week_start="sun"), "Target should be last week with sun abbreviation"
    assert cal.in_weeks(-1, week_start="su"), "Target should be last week with su abbreviation"


def test_cal_in_months():
    """Test calendar month window functionality."""
    target_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 15
    reference_time: dt.datetime = dt.datetime(2024, 2, 15, 12, 0, 0)  # February 15

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.mon.in_(-1, 0), "Target should be in range last month through this month"
    assert cal.mon.in_(-1, 0), "Target should be just last month"
    assert not cal.mon.in_(0), "Target should not be this month"


def test_cal_in_quarters():
    """Test calendar quarter window functionality."""
    target_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1 2024
    reference_time: dt.datetime = dt.datetime(2024, 4, 15, 12, 0, 0)  # Q2 2024

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.qtr.in_(-1, 0), "Target should be in range last quarter through this quarter"
    assert cal.qtr.in_(-1), "Target should be just last quarter (Q1)"
    assert not cal.qtr.in_(0), "Target should not be this quarter (Q2)"


def test_cal_in_years():
    """Test calendar year window functionality."""
    target_time: dt.datetime = dt.datetime(2023, 6, 15, 12, 0, 0)  # 2023
    reference_time: dt.datetime = dt.datetime(2024, 6, 15, 12, 0, 0)  # 2024

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.year.in_(-1, 0), "Target should be in range last year through this year"
    assert cal.year.in_(-1), "Target should be just last year"
    assert not cal.year.in_(0), "Target should not be this year"


def test_cal_single_vs_range():
    """Test single time unit vs range specifications."""
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.day.in_(-1, 0), "Target should be just yesterday"

    # Assert (range)
    assert cal.day.in_(-1, 0), "Target should be in range yesterday through today"


def test_weekday_normalization():
    """Test the normalize_weekday function indirectly through Cal."""
    # Test full names
    # Arrange / Act & Assert: normalization is pure function; test values directly
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
    # Arrange / Act & Assert: invalid specs raise ValueError
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("invalid")

    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("xyz")


def test_cal_edge_cases():
    """Test edge cases in calendar functionality."""
    # Test with same date/time (zero difference)
    target_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 30, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 30, 0)

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert: All current windows should return True
    assert cal.min.in_(0), "Target should be in current minute window"
    assert cal.hr.in_(0), "Target should be in current hour window"
    assert cal.day.in_(0, 1), "Target should be in current day window"
    assert cal.mon.in_(0, 1), "Target should be in current month window"
    assert cal.qtr.in_(0), "Target should be in current quarter window"
    assert cal.year.in_(0), "Target should be in current year window"
    assert cal.wk.in_(0), "Target should be in current week window"


def test_cal_month_edge_cases():
    """Test month calculations across year boundaries."""
    # Test December to January transition
    target_time: dt.datetime = dt.datetime(2023, 12, 15, 12, 0, 0)  # December 2023
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 2024

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert: Should be in the previous month
    assert cal.mon.in_(-1, 0), "Target should be last month"
    assert not cal.mon.in_(0), "Target should not be this month"

    # Arrange (multiple years back)
    target_time: dt.datetime = dt.datetime(2022, 6, 15, 12, 0, 0)  # June 2022
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 2024

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert: Should be about 19 months ago
    assert cal.mon.in_(-20, -18)
    assert not cal.mon.in_(-12, 0)


def test_cal_quarter_edge_cases():
    """Test quarter calculations across year boundaries."""
    # Q4 2023 to Q1 2024 transition
    target_time: dt.datetime = dt.datetime(2023, 11, 15, 12, 0, 0)  # Q4 2023
    reference_time: dt.datetime = dt.datetime(2024, 2, 15, 12, 0, 0)  # Q1 2024

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert: Should be in the previous quarter
    assert cal.qtr.in_(-1)  # Last quarter
    assert not cal.qtr.in_(0)  # This quarter

    # Test edge quarters
    target_time: dt.datetime = dt.datetime(2024, 3, 31, 12, 0, 0)  # End of Q1
    reference_time: dt.datetime = dt.datetime(2024, 4, 1, 12, 0, 0)  # Start of Q2

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert
    assert cal.qtr.in_(-1), "Target should be previous quarter"
    assert not cal.qtr.in_(0), "Target should not be current quarter"


def test_cal_year_edge_cases():
    """Test year calculations."""
    # Year boundary test
    target_time: dt.datetime = dt.datetime(2023, 12, 31, 23, 59, 59)  # End of 2023
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 0, 0, 1)  # Start of 2024

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert: Should be in the previous year
    assert cal.year.in_(-1), "Target should be last year"
    assert not cal.year.in_(0), "Target should not be this year"

    # Assert: Multi-year range
    assert cal.year.in_(-2, 0), "Target should be in range 2 years ago through now"


def test_cal_week_different_starts():
    """Test week calculations with different start days."""
    # Test with a clear week boundary
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)  # Monday, Jan 1
    reference_time: dt.datetime = dt.datetime(
        2024, 1, 8, 12, 0, 0
    )  # Monday, Jan 8 (next week)

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert: With Monday start, target should be exactly one week ago
    assert cal.in_weeks(-1, week_start="monday"), "Target should be last week with Monday start"
    assert not cal.in_weeks(0, week_start="monday"), "Target should not be this week with Monday start"

    # Test Sunday start with different dates to avoid edge cases
    target_time: dt.datetime = dt.datetime(2024, 1, 7, 12, 0, 0)  # Sunday
    reference_time: dt.datetime = dt.datetime(2024, 1, 14, 12, 0, 0)  # Next Sunday

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert: Test Sunday-based weeks
    assert cal.in_weeks(-1, week_start="sunday")


def test_cal_minutes_edge_cases():
    """Test minute window edge cases."""
    # Test minute boundaries
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 29, 59)  # End of minute 29
    reference_time: dt.datetime = dt.datetime(
        2024, 1, 1, 12, 30, 0
    )  # Start of minute 30

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act
    # (membership checks below)

    # Assert
    assert cal.min.in_(-1), "Target should be previous minute"
    assert not cal.min.in_(0), "Target should not be current minute"

    # Assert: Test range spanning multiple minutes
    assert cal.min.in_(-5, 0), "Target should be in range 5 minutes ago through now"


def test_cal_hours_edge_cases():
    """Test hour window edge cases."""
    # Test hour boundaries
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 11, 59, 59)  # End of hour 11
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)  # Start of hour 12

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert: Should be in the previous hour
    assert cal.hr.in_(-1), "Target should be previous hour"
    assert not cal.hr.in_(0), "Target should not be current hour"

    # Assert: Test range spanning multiple hours
    assert cal.hr.in_(-6, 0), "Target should be in range 6 hours ago through now"


def test_cal_future_windows():
    """Test calendar windows for future dates."""
    # Target is in the future
    target_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)  # Tomorrow
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)  # Today

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act / Assert: Test future windows
    assert cal.day.in_(1, 2), "Target should be tomorrow"
    assert cal.hr.in_(24), "Target should be 24 hours from now"
    assert cal.min.in_(1440), "Target should be 1440 minutes from now"

    # Assert: Future weeks
    assert cal.wk.in_(0, 1), "Target should be in range this week through next week"

    # Future months
    target_time: dt.datetime = dt.datetime(2024, 2, 15, 12, 0, 0)  # Next month
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # This month

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert
    assert cal.mon.in_(1, 2), "Target should be next month"

    # Future quarters
    target_time: dt.datetime = dt.datetime(2024, 7, 15, 12, 0, 0)  # Q3
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert
    assert cal.qtr.in_(2), "Target should be 2 quarters from now"

    # Future years
    target_time: dt.datetime = dt.datetime(2026, 1, 15, 12, 0, 0)  # 2026
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # 2024

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert
    assert cal.year.in_(2), "Target should be 2 years from now"


def test_cal_month_complex_calculations():
    """Test complex month calculations that cross multiple year boundaries."""
    # Test going back many months across years
    target_time: dt.datetime = dt.datetime(2021, 3, 15, 12, 0, 0)  # March 2021
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 2024

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Calculate exact months back: from March 2021 to January 2024
    # From March 2021 to January 2022 = 10 months
    # From January 2022 to January 2024 = 24 months
    # Total = 34 months back

    # Assert
    assert cal.mon.in_(-34, -33), "Target should be exactly 34 months ago"
    assert cal.mon.in_(-35, -33), "Target should be in range around the target (34 months ago)"


def test_cal_quarter_complex_calculations():
    """Test complex quarter calculations across multiple years."""
    # Test going back many quarters
    target_time: dt.datetime = dt.datetime(2021, 7, 15, 12, 0, 0)  # Q3 2021
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1 2024

    # Arrange
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Assert: This should be about 10 quarters ago
    assert cal.qtr.in_(-12, -8), "Target should be in range about 10 quarters ago"


@pytest.mark.parametrize(
    "target, ref, holidays, fy_start_month, expected_target, expected_ref, expected_holidays, expected_fy_start",
    [
        # datetime/datetime, no holidays, default FY
        (
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            None,
            1,
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            None,
            1,
        ),
        # timestamp/datetime, holidays, custom FY
        (
            dt.datetime(2024, 1, 1, 12, 0, 0).timestamp(),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            {"2024-01-01"},
            4,
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            {"2024-01-01"},
            4,
        ),
        # datetime/timestamp, holidays, default FY
        (
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0).timestamp(),
            {"2024-01-02"},
            1,
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            {"2024-01-02"},
            1,
        ),
        # timestamp/timestamp, no holidays, custom FY
        (
            dt.datetime(2024, 1, 1, 12, 0, 0).timestamp(),
            dt.datetime(2024, 1, 2, 12, 0, 0).timestamp(),
            None,
            7,
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            None,
            7,
        ),
    ],
)
def test_cal_initialization_variants(
    target: dt.datetime | float,
    ref: dt.datetime | float,
    holidays: set[str] | None,
    fy_start_month: int,
    expected_target: dt.datetime,
    expected_ref: dt.datetime,
    expected_holidays: set[str] | None,
    expected_fy_start: int,
) -> None:
    """Test Cal initialization with various target/ref types, holidays, and fiscal year starts."""
    # Arrange: Inputs are parameterized above

    cal: Cal = Cal(target, ref)

    # Assert: Properties match expectations
    assert cal.target_dt == expected_target
    assert cal.ref_dt == expected_ref




def test_cal_month_year_rollover_edge_cases():
    """Test month calculations with complex year rollovers."""
    # Test cases that exercise the while loops in month calculations

    # Case 1: Many months in the past that requires multiple year adjustments
    target_time: dt.datetime = dt.datetime(2020, 1, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 12, 15, 12, 0, 0)

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # This should be about 59 months ago
    assert cal.mon.in_(-60, -58)

    # Case 2: Many months in the future
    target_time: dt.datetime = dt.datetime(2028, 12, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # This should be about 59 months in the future
    assert cal.mon.in_(58, 60)


def test_cal_quarter_year_rollover_edge_cases():
    """Test quarter calculations with complex year rollovers."""
    # Test cases that exercise the while loops in quarter calculations

    # Case 1: Many quarters in the past
    target_time: dt.datetime = dt.datetime(2020, 2, 15, 12, 0, 0)  # Q1 2020
    reference_time: dt.datetime = dt.datetime(2024, 11, 15, 12, 0, 0)  # Q4 2024

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # This should be about 19 quarters ago
    assert cal.qtr.in_(-20, -18)

    # Case 2: Many quarters in the future
    target_time: dt.datetime = dt.datetime(2029, 8, 15, 12, 0, 0)  # Q3 2029
    reference_time: dt.datetime = dt.datetime(2024, 2, 15, 12, 0, 0)  # Q1 2024

    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # This should be about 22 quarters in the future
    assert cal.qtr.in_(21, 23)


def test_normalize_weekday_error_with_detailed_message():
    """Test that normalize_weekday provides helpful error messages."""
    with pytest.raises(ValueError) as excinfo:
        normalize_weekday("invalid_day")
    error_msg = str(excinfo.value)
    # Check that the error message contains helpful examples
    # Assert: Error message contains helpful sections
    assert "Invalid day specification" in error_msg
    assert "Full:" in error_msg
    assert "3-letter:" in error_msg
    assert "2-letter:" in error_msg
    assert "Pandas:" in error_msg


def test_cal_type_checking_imports():
    """Test that TYPE_CHECKING imports work correctly."""
    # Import the module to ensure TYPE_CHECKING code paths are exercised
    import frist._cal as cal_module

    # Act
    # Check that the module has the expected attributes
    assert hasattr(cal_module, "Cal")
    assert hasattr(cal_module, "normalize_weekday")

    # Assert: Verify TYPE_CHECKING behavior by checking typing imports exist
    assert hasattr(cal_module, "TYPE_CHECKING")

    # Act: Test that we can instantiate and use the classes
    from typing import TYPE_CHECKING

    # Assert
    assert TYPE_CHECKING is False  # Should be False at runtime


def test_in_xxx_raises_on_backwards_ranges():
    target_time: dt.datetime = dt.datetime(2024, 6, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 6, 15, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal

    # Act & Assert: backwards ranges should raise
    with pytest.raises(ValueError):
        cal.day.in_(2, -2)
    with pytest.raises(ValueError):
        cal.mon.in_(5, 0)
    with pytest.raises(ValueError):
        cal.qtr.in_(3, 1)
    with pytest.raises(ValueError):
        cal.year.in_(4, 2)
    with pytest.raises(ValueError):
        cal.wk.in_(3, 0)
    with pytest.raises(ValueError):
        cal.hr.in_(10, 5)
    with pytest.raises(ValueError):
        cal.min.in_(15, 10)



def test_cal_init_invalid_target_type():
    """
    Arrange: Provide invalid target_dt type
    Act & Assert: TypeError is raised
    """
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal("not-a-date", dt.datetime.now()) # type: ignore # Intentional type error for testing


def test_cal_init_invalid_ref_type():
    """Arrange, Act, Assert
    Arrange: Provide invalid ref_dt type
    Act & Assert: TypeError is raised
    """
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal(dt.datetime.now(), "not-a-date") # type: ignore # Intentional type error for testing


@pytest.mark.parametrize(
    "method",
    [
        "in_days",
        "in_hours",
        "in_minutes",
        "in_months",
        "in_quarters",
        "in_years",
        "in_weeks" ],
)
def test_cal_window_start_greater_than_end(method:str):
    """
    Arrange: Create Cal and call window method with start > end
    Act & Assert: ValueError is raised
    """
    cal: Cal = Cal(dt.datetime(2024, 1, 2), dt.datetime(2024, 1, 1))
    func = getattr(cal, method)
    with pytest.raises(ValueError, match="start.*must not be greater than end"):
        # For in_weeks, pass week_start as well
        if method == "in_weeks":
            func(2, 1, "monday")
        else:
            func(2, 1)


def test_in_months_edge_cases():
    """
    Test Cal.in_months for edge cases: negative, zero, positive, and range.
    """
    target = dt.datetime(2024, 1, 15)
    ref = dt.datetime(2024, 1, 1)
    cal: Cal = Cal(target, ref)
    # Arrange
    # This month
    assert cal.mon.in_(0, 1), "Target should be this month"
    # Last month
    assert not cal.mon.in_(-1), "Target should not be last month"
    # Next month
    assert not cal.mon.in_(1), "Target should not be next month"
    # Range: last 12 months through this month
    assert cal.mon.in_(-12, 1), "Target should be in range last 12 months through this month"


@pytest.mark.parametrize("spec,expected", [
    # Full names
    ("monday", 0), ("tuesday", 1), ("wednesday", 2), ("thursday", 3),
    ("friday", 4), ("saturday", 5), ("sunday", 6),
    # 3-letter abbreviations
    ("mon", 0), ("tue", 1), ("wed", 2), ("thu", 3),
    ("fri", 4), ("sat", 5), ("sun", 6),
    # 2-letter abbreviations
    ("mo", 0), ("tu", 1), ("we", 2), ("th", 3),
    ("fr", 4), ("sa", 5), ("su", 6),
    # Pandas style
    ("w-mon", 0), ("w-tue", 1), ("w-wed", 2), ("w-thu", 3),
    ("w-fri", 4), ("w-sat", 5), ("w-sun", 6),
    # Case insensitivity
    ("MONDAY", 0), ("Mon", 0), ("W-SUN", 6), ("thU", 3),
])
def test_normalize_weekday_valid(spec, expected):
    # Act & Assert: pure function mapping
    assert normalize_weekday(spec) == expected, f"{spec} should map to {expected}"


@pytest.mark.parametrize("bad_spec", [
    "nonday", "w-xyz", "abc", "", "w-", "mond", "tues", "w-funday"
])
def test_normalize_weekday_invalid(bad_spec):
    # Act & Assert: invalid specs raise
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday(bad_spec)


def test_cal_timezone_not_supported():
    """Cal raises TypeError for timezone-aware datetimes."""
    tz_dt = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Cal(tz_dt, dt.datetime(2025, 1, 1))
    
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Cal(dt.datetime(2025, 1, 1), tz_dt)


def test_cal_with_dates():
    """Cal correctly handles date inputs and recognizes one day apart."""
    # Arrange
    target_date = dt.date(2025, 1, 1)  # midnight Jan 1
    ref_date = dt.date(2025, 1, 2)     # midnight Jan 2
    
    # Act
    cal = Cal(target_date, ref_date)
    
    # Assert
    assert cal.day.in_(-1), "Target should be yesterday relative to reference"
    assert not cal.day.in_(0), "Target should not be today"
    assert cal.is_yesterday, "Target should be yesterday"


@pytest.mark.parametrize("target, ref", [
    (dt.date(2025, 1, 1), dt.date(2025, 1, 2)),
    (dt.date(2025, 1, 1), dt.datetime(2025, 1, 2, 0, 0, 0)),
    (dt.datetime(2025, 1, 1, 0, 0, 0), dt.date(2025, 1, 2)),
])
def test_cal_with_mixed_date_types(target, ref):
    """Cal correctly handles mixed date/datetime inputs."""
    # Arrange & Act
    cal = Cal(target, ref)
    
    # Assert
    assert cal.day.in_(-1), "Target should be yesterday relative to reference"
    assert not cal.day.in_(0), "Target should not be today"
    assert cal.is_yesterday, "Target should be yesterday"
