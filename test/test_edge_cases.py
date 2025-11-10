"""
Edge cases, error handling, and parameter validation tests for Zeit/Cal.
"""

import datetime as dt

import pytest

from frist import Frist


def test_in_days_backwards_range():
    target_time = dt.datetime(2024, 1, 1)
    reference_time = dt.datetime(2024, 1, 2)
    z = Frist(target_time=target_time, reference_time=reference_time)
    cal = z.cal
    with pytest.raises(ValueError):
        cal.in_days(2, -2)


def test_zeit_invalid_fy_start_month():
    """Test invalid fiscal year start month."""
    target_time = dt.datetime(2024, 1, 1)
    with pytest.raises(ValueError):
        Frist(target_time=target_time, fy_start_month=0)  # Invalid month
    with pytest.raises(ValueError):
        Frist(target_time=target_time, fy_start_month=13)  # Invalid month


def test_malformed_holidays():
    """Test malformed holiday sets."""
    target_time = dt.datetime(2024, 1, 1)
    # Invalid date format in holidays
    holidays = {"2024-13-45", "invalid-date"}  # Invalid dates
    z = Frist(target_time=target_time, holidays=holidays)
    # Should not crash, just not match
    assert z.cal.holiday is False


def test_in_qtr_invalid_ranges():
    """Test in_qtr with invalid parameter ranges."""
    target_time = dt.datetime(2024, 1, 1)
    reference_time = dt.datetime(2024, 4, 1)
    Frist(target_time=target_time, reference_time=reference_time)



def test_in_fiscal_qtr_invalid_ranges():
    """Test in_fiscal_qtr with invalid parameter ranges."""
    target_time = dt.datetime(2024, 1, 1)
    reference_time = dt.datetime(2024, 4, 1)
    Frist(target_time=target_time, reference_time=reference_time, fy_start_month=4)



def test_boundary_dates():
    """Test boundary conditions for dates."""
    # Leap year boundary
    target_time = dt.datetime(2024, 2, 29)  # Leap day
    reference_time = dt.datetime(2024, 3, 1)
    Frist(target_time=target_time, reference_time=reference_time)

    # Year boundary
    target_time = dt.datetime(2023, 12, 31, 23, 59, 59)
    reference_time = dt.datetime(2024, 1, 1, 0, 0, 1)
    Frist(target_time=target_time, reference_time=reference_time)


def test_large_time_differences():
    """Test large time differences in *_ago properties."""
    target_time = dt.datetime(2000, 1, 1)
    reference_time = dt.datetime(2024, 1, 1)
    z = Frist(target_time=target_time, reference_time=reference_time)

    # Should handle large differences without overflow
    expected_years: float = 24.0
    assert z.age.years == pytest.approx(expected_years, rel=0.01)




def test_parse_edge_cases():
    """Test .parse with edge cases."""
    # Very large timestamp
    large_timestamp = "2147483647"  # Max 32-bit int
    z = Frist.parse(large_timestamp)
    assert z.target_time.year >= 2038

    # Empty string
    with pytest.raises(ValueError):
        Frist.parse("")

    # Whitespace only
    z_ws = Frist.parse("  2024-01-01  ")
    assert z_ws.target_time.year == 2024


def test_fiscal_boundary_crossing():
    """Test fiscal year/quarter boundaries."""
    # Fiscal year starting in July
    target_time = dt.datetime(2024, 6, 30)  # June 2024
    z = Frist(target_time=target_time, fy_start_month=7)
    assert z.cal.fiscal_year == 2023  # Before July start
    assert z.cal.fiscal_quarter == 4  # Q4 for July start

    target_time = dt.datetime(2024, 7, 1)  # July 2024
    z = Frist(target_time=target_time, fy_start_month=7)
    assert z.cal.fiscal_year == 2024
    assert z.cal.fiscal_quarter == 1


def test_min_max_datetime():
    # Minimum datetime
    min_dt = dt.datetime.min.replace(microsecond=0)
    max_dt = dt.datetime.max.replace(microsecond=0)
    z_min = Frist(target_time=min_dt)
    z_max = Frist(target_time=max_dt)
    assert z_min.target_time == min_dt
    assert z_max.target_time == max_dt


def test_microsecond_precision():
    # Microsecond edge
    dt1 = dt.datetime(2024, 1, 1, 12, 0, 0, 0)
    dt2 = dt.datetime(2024, 1, 1, 12, 0, 0, 999999)
    z1 = Frist(target_time=dt1)
    z2 = Frist(target_time=dt2)
    assert z2.target_time.microsecond == 999999
    assert z1.target_time.microsecond == 0


def test_timezone_aware_naive():
    # Naive datetime
    naive_dt = dt.datetime(2024, 1, 1, 12, 0, 0)
    z_naive = Frist(target_time=naive_dt)
    assert z_naive.target_time.tzinfo is None
    # Aware datetime
    aware_dt = dt.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)
    z_aware = Frist(target_time=aware_dt)
    assert z_aware.target_time.tzinfo is not None


def test_invalid_input():
    # Non-datetime input should raise
    with pytest.raises(ValueError):
        Frist(target_time="2024-01-01")
    # Extreme year out of range
    with pytest.raises(ValueError):
        Frist(target_time=dt.datetime(10000, 1, 1))


def test_leap_year():
    # Leap year Feb 29
    leap_dt = dt.datetime(2024, 2, 29, 12, 0, 0)
    z = Frist(target_time=leap_dt)
    assert z.target_time.month == 2
    assert z.target_time.day == 29


def test_end_of_month_year():
    # End of month
    eom_dt = dt.datetime(2024, 1, 31, 23, 59, 59)
    z = Frist(target_time=eom_dt)
    assert z.target_time.day == 31
    # End of year
    eoy_dt = dt.datetime(2024, 12, 31, 23, 59, 59)
    z = Frist(target_time=eoy_dt)
    assert z.target_time.month == 12
    assert z.target_time.day == 31
