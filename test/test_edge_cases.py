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

from frist import BizPolicy, Chrono


def test_in_days_backwards_range():
    """Test ValueError for backwards day range."""
    # Arrange
    target_time = dt.datetime(2024, 1, 1)
    reference_time = dt.datetime(2024, 1, 2)
    z = Chrono(target_dt=target_time, ref_dt=reference_time)
    cal = z.cal
    # Act & Assert
    with pytest.raises(ValueError):
        cal.day.in_(2, -2)


def test_in_qtr_invalid_ranges():
    """Test invalid quarter parameter ranges (no assertion, just construction)."""
    # Arrange
    target_time = dt.datetime(2024, 1, 1)
    reference_time = dt.datetime(2024, 4, 1)
    # Act
    Chrono(target_dt=target_time, ref_dt=reference_time)


def test_boundary_dates():
    """Test leap year and year boundary conditions for Chrono."""
    # Arrange & Act
    # Leap year boundary
    target_time = dt.datetime(2024, 2, 29)  # Leap day
    reference_time = dt.datetime(2024, 3, 1)
    chrono_leap = Chrono(target_dt=target_time, ref_dt=reference_time)
    # Assert
    expected_year = 2024
    expected_month = 2
    expected_day = 29
    expected_days = 1
    actual_year = chrono_leap.target_dt.year
    actual_month = chrono_leap.target_dt.month
    actual_day = chrono_leap.target_dt.day
    actual_days = chrono_leap.age.days
    assert actual_year == expected_year, "Leap year should be 2024"
    assert actual_month == expected_month, "Leap month should be February"
    assert actual_day == expected_day, "Leap day should be 29"
    assert actual_days == expected_days, "Leap day to next day should be 1 day"

    # Year boundary
    target_time = dt.datetime(2023, 12, 31, 23, 59, 59)
    reference_time = dt.datetime(2024, 1, 1, 0, 0, 1)
    chrono_year = Chrono(target_dt=target_time, ref_dt=reference_time)
    expected_year = 2023
    expected_month = 12
    expected_day = 31
    expected_days = 0
    expected_seconds = 2
    actual_year = chrono_year.target_dt.year
    actual_month = chrono_year.target_dt.month
    actual_day = chrono_year.target_dt.day
    actual_days = chrono_year.age.days
    actual_seconds = chrono_year.age.seconds
    assert actual_year == expected_year, "Year should be 2023"
    assert actual_month == expected_month, "Month should be December"
    assert actual_day == expected_day, "Day should be 31"
    assert actual_days == pytest.approx(expected_days, abs=1e-4), (
        "Should be very close to 0 days (2 seconds apart)"
    )
    assert actual_seconds == expected_seconds, "Should be exactly 2 seconds apart"


def test_large_time_differences():
    """Test large time differences in age calculation."""
    # Arrange
    target_time = dt.datetime(2000, 1, 1)
    reference_time = dt.datetime(2024, 1, 1)
    # Act
    z = Chrono(target_dt=target_time, ref_dt=reference_time)
    # Assert
    expected_years: float = 24.0
    actual_years = z.age.years
    assert actual_years == pytest.approx(expected_years, rel=0.01), (
        f"Expected years approx {expected_years}, got {actual_years}"
    )  # type: ignore


def test_parse_edge_cases():
    """Test Chrono.parse edge cases (large timestamp, empty string, whitespace)."""
    # Arrange & Act
    large_timestamp = "2147483647"  # Max 32-bit int
    z = Chrono.parse(large_timestamp)
    # Assert
    expected_year = 2038
    actual_year = z.target_dt.year
    assert actual_year >= expected_year, (
        f"Expected year >= {expected_year}, got {actual_year}"
    )

    # Act & Assert
    with pytest.raises(ValueError):
        Chrono.parse("")

    # Act & Assert
    z_ws = Chrono.parse("  2024-01-01  ")
    expected_year = 2024
    actual_year = z_ws.target_dt.year
    assert actual_year == expected_year, (
        f"Expected year {expected_year}, got {actual_year}"
    )


def test_fiscal_boundary_crossing() -> None:
    """Test fiscal year/quarter boundaries using BizPolicy."""
    # Arrange
    policy_july: BizPolicy = BizPolicy(fiscal_year_start_month=7)

    # Act
    target_time_june: dt.datetime = dt.datetime(2024, 6, 30)  # June 2024
    chrono_june: Chrono = Chrono(target_dt=target_time_june, policy=policy_july)
    # Assert
    expected_fiscal_year_june = 2023
    expected_fiscal_quarter_june = 4
    actual_fiscal_year_june = chrono_june.biz.fiscal_year
    actual_fiscal_quarter_june = chrono_june.biz.fiscal_quarter
    assert actual_fiscal_year_june == expected_fiscal_year_june, (
        f"Expected fiscal year {expected_fiscal_year_june} for June, "
        f"got {actual_fiscal_year_june}"
    )
    assert actual_fiscal_quarter_june == expected_fiscal_quarter_june, (
        f"Expected fiscal quarter {expected_fiscal_quarter_june} for June, "
        f"got {actual_fiscal_quarter_june}"
    )

    # Act
    target_time_july: dt.datetime = dt.datetime(2024, 7, 1)  # July 2024
    chrono_july: Chrono = Chrono(target_dt=target_time_july, policy=policy_july)
    # Assert
    expected_fiscal_year_july = 2024
    expected_fiscal_quarter_july = 1
    actual_fiscal_year_july = chrono_july.biz.fiscal_year
    actual_fiscal_quarter_july = chrono_july.biz.fiscal_quarter
    assert actual_fiscal_year_july == expected_fiscal_year_july, (
        f"Expected fiscal year {expected_fiscal_year_july} for July, "
        f"got {actual_fiscal_year_july}"
    )
    assert actual_fiscal_quarter_july == expected_fiscal_quarter_july, (
        f"Expected fiscal quarter {expected_fiscal_quarter_july} for July, "
        f"got {actual_fiscal_quarter_july}"
    )


def test_min_max_datetime():
    """Test Chrono with min and max datetime values."""
    # Arrange
    min_dt = dt.datetime.min.replace(microsecond=0)
    max_dt = dt.datetime.max.replace(microsecond=0)
    # Act
    z_min = Chrono(target_dt=min_dt)
    z_max = Chrono(target_dt=max_dt)
    # Assert
    expected_min = min_dt
    expected_max = max_dt
    actual_min = z_min.target_dt
    actual_max = z_max.target_dt
    assert actual_min == expected_min, (
        f"Expected min datetime {expected_min}, got {actual_min}"
    )
    assert actual_max == expected_max, (
        f"Expected max datetime {expected_max}, got {actual_max}"
    )


def test_microsecond_precision():
    """Test microsecond precision in Chrono target_time."""
    # Arrange
    dt1 = dt.datetime(2024, 1, 1, 12, 0, 0, 0)
    dt2 = dt.datetime(2024, 1, 1, 12, 0, 0, 999999)
    # Act
    z1 = Chrono(target_dt=dt1)
    z2 = Chrono(target_dt=dt2)
    # Assert
    expected_microsecond_2 = 999999
    expected_microsecond_1 = 0
    actual_microsecond_2 = z2.target_dt.microsecond
    actual_microsecond_1 = z1.target_dt.microsecond
    assert actual_microsecond_2 == expected_microsecond_2, (
        f"Expected microsecond {expected_microsecond_2}, got {actual_microsecond_2}"
    )
    assert actual_microsecond_1 == expected_microsecond_1, (
        f"Expected microsecond {expected_microsecond_1}, got {actual_microsecond_1}"
    )


def test_timezone_aware_naive():
    """Test timezone awareness for naive and aware datetimes in Chrono."""
    # Arrange
    naive_dt = dt.datetime(2024, 1, 1, 12, 0, 0)
    aware_dt = dt.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)
    # Act
    z_naive = Chrono(target_dt=naive_dt)
    # Assert
    expected_tzinfo = None
    actual_tzinfo = z_naive.target_dt.tzinfo
    assert actual_tzinfo is expected_tzinfo, (
        "Expected tzinfo to be None for naive datetime"
    )
    # Timezone-aware datetimes should raise TypeError
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Chrono(target_dt=aware_dt)


def test_invalid_input():
    """Test invalid input handling for Chrono."""
    # Arrange, Act & Assert
    # Non-datetime input should raise
    with pytest.raises(TypeError):
        Chrono(target_dt={"1": "one"})  # type: ignore # Intentional wrong type for test
    # Extreme year out of range
    with pytest.raises(ValueError):
        Chrono(target_dt=dt.datetime(10000, 1, 1))


def test_leap_year():
    """Test leap year Feb 29 handling in Chrono."""
    # Arrange
    leap_dt = dt.datetime(2024, 2, 29, 12, 0, 0)
    # Act
    z = Chrono(target_dt=leap_dt)
    # Assert
    expected_month = 2
    expected_day = 29
    actual_month = z.target_dt.month
    actual_day = z.target_dt.day
    assert actual_month == expected_month, (
        f"Expected month {expected_month} for leap year, got {actual_month}"
    )
    assert actual_day == expected_day, (
        f"Expected day {expected_day} for leap year, got {actual_day}"
    )


def test_end_of_month_year():
    """Test end-of-month and end-of-year handling in Chrono."""
    # Arrange
    eom_dt = dt.datetime(2024, 1, 31, 23, 59, 59)
    eoy_dt = dt.datetime(2024, 12, 31, 23, 59, 59)
    # Act
    z_eom = Chrono(target_dt=eom_dt)
    z_eoy = Chrono(target_dt=eoy_dt)
    # Assert
    expected_eom_day = 31
    expected_eoy_month = 12
    expected_eoy_day = 31
    actual_eom_day = z_eom.target_dt.day
    actual_eoy_month = z_eoy.target_dt.month
    actual_eoy_day = z_eoy.target_dt.day
    assert actual_eom_day == expected_eom_day, (
        f"Expected day {expected_eom_day} for end of month, got {actual_eom_day}"
    )
    assert actual_eoy_month == expected_eoy_month, (
        f"Expected month {expected_eoy_month} for end of year, got {actual_eoy_month}"
    )
    assert actual_eoy_day == expected_eoy_day, (
        f"Expected day {expected_eoy_day} for end of year, got {actual_eoy_day}"
    )


@pytest.mark.parametrize(
    "string_input, expected_datetime",
    [
        # Format 1: YYYY-MM-DD HH:MM:SS
        ("2024-01-15 14:30:45", dt.datetime(2024, 1, 15, 14, 30, 45)),
        # Format 2: YYYY-MM-DD (date only)
        ("2024-01-15", dt.datetime(2024, 1, 15, 0, 0, 0)),
        # Format 3: ISO 8601 datetime
        ("2024-01-15T14:30:45", dt.datetime(2024, 1, 15, 14, 30, 45)),
        # Format 4: ISO 8601 UTC with Z
        ("2024-01-15T14:30:45Z", dt.datetime(2024, 1, 15, 14, 30, 45)),
    ],
)
def test_string_datetime_formats_chrono_parse(string_input, expected_datetime):
    """Test that Chrono.parse accepts all supported string datetime formats."""
    # Arrange
    ref_dt = dt.datetime(2024, 1, 16, 12, 0, 0)
    # Act
    chrono = Chrono.parse(string_input, reference_time=ref_dt)
    # Assert
    expected_target = expected_datetime
    expected_ref = ref_dt
    actual_target = chrono.target_dt
    actual_ref = chrono.ref_dt
    assert actual_target == expected_target, (
        f"Chrono.parse failed to parse {string_input}"
    )
    assert actual_ref == expected_ref, (
        f"Reference time should be preserved for {string_input}"
    )
