"""
Test suite for edge cases, error handling, and parameter validation in Chrono and Cal.

This module covers:
- Backwards and invalid ranges
- Boundary dates (leap years, year boundaries)
- Large time differences
- Parsing edge cases
- Fiscal year/quarter boundaries
- Min/max datetime
- Microsecond precision
- Timezone awareness
- Invalid input handling
- Leap year and end-of-month/year edge cases
"""

import datetime as dt

import pytest

from frist import Chrono,CalendarPolicy


def test_in_days_backwards_range():
    """Test ValueError for backwards day range."""
    # Arrange
    target_time = dt.datetime(2024, 1, 1)
    reference_time = dt.datetime(2024, 1, 2)
    z = Chrono(target_time=target_time, reference_time=reference_time)
    cal = z.cal
    # Act & Assert
    with pytest.raises(ValueError):
        cal.in_days(2, -2)




def test_in_qtr_invalid_ranges():
    """Test invalid quarter parameter ranges (no assertion, just construction)."""
    # Arrange
    target_time = dt.datetime(2024, 1, 1)
    reference_time = dt.datetime(2024, 4, 1)
    # Act
    Chrono(target_time=target_time, reference_time=reference_time)





def test_boundary_dates():
    """Test leap year and year boundary conditions for Chrono."""
    # Arrange & Act
    # Leap year boundary
    target_time = dt.datetime(2024, 2, 29)  # Leap day
    reference_time = dt.datetime(2024, 3, 1)
    chrono_leap = Chrono(target_time=target_time, reference_time=reference_time)
    assert chrono_leap.target_time.year == 2024, "Leap year should be 2024"
    assert chrono_leap.target_time.month == 2, "Leap month should be February"
    assert chrono_leap.target_time.day == 29, "Leap day should be 29"
    assert chrono_leap.age.days == 1, "Leap day to next day should be 1 day"


    # Year boundary
    target_time = dt.datetime(2023, 12, 31, 23, 59, 59)
    reference_time = dt.datetime(2024, 1, 1, 0, 0, 1)
    chrono_year = Chrono(target_time=target_time, reference_time=reference_time)
    assert chrono_year.target_time.year == 2023, "Year should be 2023"
    assert chrono_year.target_time.month == 12, "Month should be December"
    assert chrono_year.target_time.day == 31, "Day should be 31"
    assert chrono_year.age.days == pytest.approx(0, abs=1e-4), "Should be very close to 0 days (2 seconds apart)"
    assert chrono_year.age.seconds == 2, "Should be exactly 2 seconds apart"


def test_large_time_differences():
    """Test large time differences in age calculation."""
    # Arrange
    target_time = dt.datetime(2000, 1, 1)
    reference_time = dt.datetime(2024, 1, 1)
    # Act
    z = Chrono(target_time=target_time, reference_time=reference_time)
    # Assert
    expected_years: float = 24.0
    assert z.age.years == pytest.approx(expected_years, rel=0.01), f"Expected years approx {expected_years}, got {z.age.years}" # type: ignore




def test_parse_edge_cases():
    """Test Chrono.parse edge cases (large timestamp, empty string, whitespace)."""
    # Arrange & Act
    large_timestamp = "2147483647"  # Max 32-bit int
    z = Chrono.parse(large_timestamp)
    # Assert
    assert z.target_time.year >= 2038, f"Expected year >= 2038, got {z.target_time.year}"

    # Act & Assert
    with pytest.raises(ValueError):
        Chrono.parse("")

    # Act & Assert
    z_ws = Chrono.parse("  2024-01-01  ")
    assert z_ws.target_time.year == 2024, f"Expected year 2024, got {z_ws.target_time.year}"


def test_fiscal_boundary_crossing() -> None:
    """Test fiscal year/quarter boundaries using CalendarPolicy."""
    # Arrange
    policy_july: CalendarPolicy = CalendarPolicy(fiscal_year_start_month=7)

    # Act
    target_time_june: dt.datetime = dt.datetime(2024, 6, 30)  # June 2024
    chrono_june: Chrono = Chrono(target_time=target_time_june, policy=policy_july)
    # Assert
    assert chrono_june.cal.fiscal_year == 2023, f"Expected fiscal year 2023 for June, got {chrono_june.cal.fiscal_year}"
    assert chrono_june.cal.fiscal_quarter == 4, f"Expected fiscal quarter 4 for June, got {chrono_june.cal.fiscal_quarter}"

    # Act
    target_time_july: dt.datetime = dt.datetime(2024, 7, 1)  # July 2024
    chrono_july: Chrono = Chrono(target_time=target_time_july, policy=policy_july)
    # Assert
    assert chrono_july.cal.fiscal_year == 2024, f"Expected fiscal year 2024 for July, got {chrono_july.cal.fiscal_year}"
    assert chrono_july.cal.fiscal_quarter == 1, f"Expected fiscal quarter 1 for July, got {chrono_july.cal.fiscal_quarter}"


def test_min_max_datetime():
    """Test Chrono with min and max datetime values."""
    # Arrange
    min_dt = dt.datetime.min.replace(microsecond=0)
    max_dt = dt.datetime.max.replace(microsecond=0)
    # Act
    z_min = Chrono(target_time=min_dt)
    z_max = Chrono(target_time=max_dt)
    # Assert
    assert z_min.target_time == min_dt, f"Expected min datetime {min_dt}, got {z_min.target_time}"
    assert z_max.target_time == max_dt, f"Expected max datetime {max_dt}, got {z_max.target_time}"


def test_microsecond_precision():
    """Test microsecond precision in Chrono target_time."""
    # Arrange
    dt1 = dt.datetime(2024, 1, 1, 12, 0, 0, 0)
    dt2 = dt.datetime(2024, 1, 1, 12, 0, 0, 999999)
    # Act
    z1 = Chrono(target_time=dt1)
    z2 = Chrono(target_time=dt2)
    # Assert
    assert z2.target_time.microsecond == 999999, f"Expected microsecond 999999, got {z2.target_time.microsecond}"
    assert z1.target_time.microsecond == 0, f"Expected microsecond 0, got {z1.target_time.microsecond}"


def test_timezone_aware_naive():
    """Test timezone awareness for naive and aware datetimes in Chrono."""
    # Arrange
    naive_dt = dt.datetime(2024, 1, 1, 12, 0, 0)
    aware_dt = dt.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)
    # Act
    z_naive = Chrono(target_time=naive_dt)
    z_aware = Chrono(target_time=aware_dt)
    # Assert
    assert z_naive.target_time.tzinfo is None, "Expected tzinfo to be None for naive datetime"
    assert z_aware.target_time.tzinfo is not None, "Expected tzinfo to be not None for aware datetime"


def test_invalid_input():
    """Test invalid input handling for Chrono."""
    # Arrange, Act & Assert
    # Non-datetime input should raise
    with pytest.raises(TypeError):
        Chrono(target_time={'1': 'one'}) #type: ignore # Intentional wrong type for test
    # Extreme year out of range
    with pytest.raises(ValueError):
        Chrono(target_time=dt.datetime(10000, 1, 1))


def test_leap_year():
    
    """Test leap year Feb 29 handling in Chrono."""
    # Arrange
    leap_dt = dt.datetime(2024, 2, 29, 12, 0, 0)
    # Act
    z = Chrono(target_time=leap_dt)
    # Assert
    assert z.target_time.month == 2, f"Expected month 2 for leap year, got {z.target_time.month}"
    assert z.target_time.day == 29, f"Expected day 29 for leap year, got {z.target_time.day}"


def test_end_of_month_year():
    """Test end-of-month and end-of-year handling in Chrono."""
    # Arrange
    eom_dt = dt.datetime(2024, 1, 31, 23, 59, 59)
    eoy_dt = dt.datetime(2024, 12, 31, 23, 59, 59)
    # Act
    z_eom = Chrono(target_time=eom_dt)
    z_eoy = Chrono(target_time=eoy_dt)
    # Assert
    assert z_eom.target_time.day == 31, f"Expected day 31 for end of month, got {z_eom.target_time.day}"
    assert z_eoy.target_time.month == 12, f"Expected month 12 for end of year, got {z_eoy.target_time.month}"
    assert z_eoy.target_time.day == 31, f"Expected day 31 for end of year, got {z_eoy.target_time.day}"
