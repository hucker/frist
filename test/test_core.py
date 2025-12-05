"""
Test file for standalone Chrono and time_pair functionality.

Tests Chrono and time_pair as standalone dt.datetime utilities without file dependencies.
"""

import datetime as dt

import pytest
from pytest import approx

from frist._biz_policy import BizPolicy
from frist._frist import Age, Cal, Chrono, time_pair


def test_time_pair_datetime() -> None:
    """Test time_pair with datetime objects."""
    # Arrange
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_tim, end_time=reference_tim)
    # Assert
    expected_target_tim = target_tim
    expected_reference_tim = reference_tim
    assert actual_target_tim == expected_target_tim, f"Expected target {expected_target_tim}, got {actual_target_tim}"
    assert actual_reference_tim == expected_reference_tim, f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"

def test_time_pair_date() -> None:
    """Test time_pair with date objects."""
    # Arrange
    target_dt: dt.date = dt.date(2024, 1, 1)
    reference_dt: dt.date = dt.date(2024, 1, 2)
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_dt, end_time=reference_dt)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1)
    expected_reference_tim = dt.datetime(2024, 1, 2)
    assert actual_target_tim == expected_target_tim, f"Expected target {expected_target_tim}, got {actual_target_tim}"
    assert actual_reference_tim == expected_reference_tim, f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"

def test_time_pair_float_timestamp() -> None:
    """Test time_pair with float timestamps."""
    # Arrange
    target_ts: float = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    reference_ts: float = dt.datetime(2024, 1, 2, 12, 0, 0).timestamp()
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_ts, end_time=reference_ts)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 12, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 12, 0, 0)
    assert actual_target_tim == expected_target_tim, f"Expected target {expected_target_tim}, got {actual_target_tim}"
    assert actual_reference_tim == expected_reference_tim, f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"

def test_time_pair_int_timestamp() -> None:
    """Test time_pair with int timestamps."""
    # Arrange
    target_ts: int = int(dt.datetime(2024, 1, 1, 12, 0, 0).timestamp())
    reference_ts: int = int(dt.datetime(2024, 1, 2, 12, 0, 0).timestamp())
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_ts, end_time=reference_ts)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 12, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 12, 0, 0)
    assert actual_target_tim == expected_target_tim, f"Expected target {expected_target_tim}, got {actual_target_tim}"
    assert actual_reference_tim == expected_reference_tim, f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"

def test_time_pair_string_datetime() -> None:
    """Test time_pair with string full datetime."""
    # Arrange
    start_str: str = "2024-01-01 12:00:00"
    end_str: str = "2024-01-02 12:00:00"
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=start_str, end_time=end_str)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 12, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 12, 0, 0)
    assert actual_target_tim == expected_target_tim, f"Expected target {expected_target_tim}, got {actual_target_tim}"
    assert actual_reference_tim == expected_reference_tim, f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"

def test_time_pair_string_date() -> None:
    """Test time_pair with string date only."""
    # Arrange
    start_str: str = "2024-01-01"
    end_str: str = "2024-01-02"
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=start_str, end_time=end_str)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 0, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 0, 0, 0)
    assert actual_target_tim == expected_target_tim, f"Expected target {expected_target_tim}, got {actual_target_tim}"
    assert actual_reference_tim == expected_reference_tim, f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"

def test_time_pair_end_time_none_defaults_to_now() -> None:
    """Test time_pair with end_time=None defaults to now."""
    # Arrange
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_tim, end_time=None)
    # Assert
    expected_target_tim = target_tim
    assert actual_target_tim == expected_target_tim, f"Expected target {expected_target_tim}, got {actual_target_tim}"
    assert isinstance(actual_reference_tim, dt.datetime), f"Expected reference to be datetime, got {type(actual_reference_tim)}"

def test_time_pair_start_time_none_raises() -> None:
    """Test time_pair with start_time=None raises TypeError."""
    # Arrange
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act & Assert
    with pytest.raises(TypeError):
        time_pair(start_time=None, end_time=reference_tim)

def test_time_pair_unsupported_type_raises() -> None:
    """Test time_pair with unsupported type raises TypeError."""
    # Arrange
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act & Assert
    with pytest.raises(TypeError):
        time_pair(start_time=[2024, 1, 1], end_time=reference_tim)

def test_time_pair_unsupported_string_format_raises() -> None:
    """Test time_pair with unsupported string format raises TypeError."""
    # Arrange
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act & Assert
    with pytest.raises(TypeError):
        time_pair(start_time="not-a-date", end_time=reference_tim)

def test_chrono_creation():
    """Test basic Chrono object creation."""
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)

    # Test with explicit reference time
    z: Chrono = Chrono(target_dt=target_tim, ref_dt=reference_tim)
    assert z.target_dt == target_tim
    assert z.ref_dt == reference_tim

    # Test with default reference time (now)
    chrono_now: Chrono = Chrono(target_dt=target_tim)

    assert chrono_now.target_dt == target_tim
    assert chrono_now.ref_dt is not None


def test_chrono_properties():
    """Test Chrono object properties."""
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)

    z: Chrono = Chrono(target_dt=target_tim, ref_dt=reference_tim)

    # Test basic properties
    assert z.timestamp == target_tim.timestamp()



def test_chrono_age_property():
    """Test that Chrono age property works correctly."""
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)

    z: Chrono = Chrono(target_dt=target_tim, ref_dt=reference_tim)
    age: Age = z.age

    # Test that age calculations work
    assert age.seconds == 86400.0
    assert age.minutes == 1440.0
    assert age.hours == 24.0
    assert age.days == 1.0
    assert age.weeks == pytest.approx(1.0 / 7.0) # type: ignore


def test_chrono_calendar_property():
    """Test that Chrono calendar property works correctly."""
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_tim: dt.datetime = dt.datetime(2024, 1, 1, 18, 0, 0)  # Same day, 6 hours later

    z: Chrono = Chrono(target_dt=target_tim, ref_dt=reference_tim)
    cal: Cal = z.cal

    # Test calendar window functionality
    assert cal.day.in_(0, 1)  # Same day (half-open: 0..1)
    assert cal.hour.in_(-6, 0)  # Within 6 hours
    assert not cal.day.in_(-1)  # Not yesterday


def test_chrono_with_reference_time():
    """Test creating new Chrono with different reference time."""
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    original_ref_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    new_ref_tim: dt.datetime = dt.datetime(2024, 1, 3, 12, 0, 0)

    chrono1: Chrono = Chrono(target_dt=target_tim, ref_dt=original_ref_tim)
    chrono2: Chrono = chrono1.with_reference_time(new_ref_tim)

    # Original should be unchanged
    assert chrono1.ref_dt == original_ref_tim

    # New one should have different reference
    assert chrono2.ref_dt == new_ref_tim
    assert chrono2.target_dt == target_tim  # Same target


def test_chrono_string_representations():
    """Test string representations of Chrono objects."""
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 30, 45)
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)

    z: Chrono = Chrono(target_dt=target_tim, ref_dt=reference_tim)

    # Test __repr__
    repr_str: str = repr(z)
    assert "Chrono" in repr_str
    assert "2024-01-01T12:30:45" in repr_str
    assert "2024-01-02T12:00:00" in repr_str

    # Test __str__
    str_str: str = str(z)
    assert "Chrono for 2024-01-01 12:30:45" in str_str


def test_chrono_parse_static_method():
    """Test Chrono.parse static method."""
    # Test Unix timestamp
    chrono1: Chrono = Chrono.parse("1704110400")  # 2024-01-01 12:00:00 UTC
    assert chrono1.target_dt.year == 2024
    assert chrono1.target_dt.month == 1
    assert chrono1.target_dt.day == 1

    # Test ISO format
    chrono2: Chrono = Chrono.parse("2024-01-01T12:30:00")
    assert chrono2.target_dt.hour == 12
    assert chrono2.target_dt.minute == 30

    # Test simple date
    chrono3: Chrono = Chrono.parse("2024-12-25")
    assert chrono3.target_dt.month == 12
    assert chrono3.target_dt.day == 25

    # Test with custom reference time
    ref_tim: dt.datetime = dt.datetime(2024, 6, 1)
    chrono4: Chrono = Chrono.parse("2024-01-01", ref_tim)
    assert chrono4.ref_dt == ref_tim


def test_chrono_parse_errors():
    """Test Chrono.parse error handling."""
    with pytest.raises(ValueError, match="Unable to parse time string"):
        Chrono.parse("invalid-date-format")

    with pytest.raises(ValueError, match="Unable to parse time string"):
        Chrono.parse("not-a-date-at-all")


def test_chrono_fiscal_properties():
    """Test fiscal year and quarter properties."""
    # Default fiscal year (starts in January)
    target_tim: dt.datetime = dt.datetime(2024, 2, 15)
    z: Chrono = Chrono(target_dt=target_tim)
    assert z.biz.fiscal_year == 2024
    assert z.biz.fiscal_quarter == 1  # Jan-Mar

    # Fiscal year starting in April using BizPolicy
    policy_april: BizPolicy = BizPolicy(fiscal_year_start_month=4)
    chrono_april: Chrono = Chrono(target_dt=target_tim, policy=policy_april)
    assert chrono_april.biz.fiscal_year == 2023  # Feb is before April start
    assert chrono_april.biz.fiscal_quarter == 4  # Jan-Mar is Q4 for April start

    target_tim_july: dt.datetime = dt.datetime(2024, 7, 15)
    chrono_july: Chrono = Chrono(target_dt=target_tim_july, policy=policy_april)
    assert chrono_july.biz.fiscal_year == 2024
    assert chrono_july.biz.fiscal_quarter == 2  # Jul-Sep is Q2 for April start


def test_chrono_holiday_property():
    """Test holiday detection property."""
    policy: BizPolicy = BizPolicy(holidays={"2024-01-01", "2024-12-25"})

    target_tim: dt.datetime = dt.datetime(2024, 1, 1)
    chrono: Chrono = Chrono(target_dt=target_tim, policy=policy)
    assert chrono.biz.holiday is True

    target_tim_not_holiday: dt.datetime = dt.datetime(2024, 7, 4)
    chrono_not: Chrono = Chrono(target_dt=target_tim_not_holiday, policy=policy)
    assert chrono_not.biz.holiday is False

    # Empty holidays
    empty_policy: BizPolicy = BizPolicy(holidays=set())
    chrono_empty: Chrono = Chrono(target_dt=target_tim, policy=empty_policy)
    assert chrono_empty.biz.holiday is False


@pytest.mark.parametrize(
    "input_type",
    ["datetime", "float", "int", "str_datetime"],
)
def test_age_equivalent_inputs_produce_same_results(input_type: str) -> None:
    """
    Test that equivalent TimeLike representations of the same instant produce identical Age calculations.
    
    This tests that datetime, timestamp (float/int), and string representations of the same time
    all produce identical Age objects and calculations.
    """
    # Arrange: Define reference times with specific time components
    start_dt = dt.datetime(2020, 6, 15, 14, 30, 45)
    end_dt = dt.datetime(2023, 9, 22, 9, 15, 30)
    
    # Convert to equivalent representations
    time_formats = {
        "datetime": start_dt,
        "float": start_dt.timestamp(),
        "int": int(start_dt.timestamp()),
        "str_datetime": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    end_time_formats = {
        "datetime": end_dt,
        "float": end_dt.timestamp(),
        "int": int(end_dt.timestamp()),
        "str_datetime": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    start_input = time_formats[input_type]
    end_input = end_time_formats[input_type]
    
    # Act: Create Age object
    age = Age(start_input, end_input)
    
    # Assert: Results should be identical to reference datetime Age
    reference_age = Age(start_dt, end_dt)
    
    assert age.days == approx(reference_age.days, rel=1e-10), f"Days differ for {input_type}"
    assert age.seconds == reference_age.seconds, f"Seconds differ for {input_type}"
    assert age.years_precise == approx(reference_age.years_precise, rel=1e-10), f"Years precise differ for {input_type}"
    assert age.months_precise == approx(reference_age.months_precise, rel=1e-10), f"Months precise differ for {input_type}"


@pytest.mark.parametrize(
    "input_type",
    ["date", "str_date"],
)
def test_age_midnight_inputs_produce_same_results(input_type: str) -> None:
    """
    Test that date and date-string representations (both midnight) produce identical Age calculations.
    """
    # Arrange: Define reference times at midnight
    start_dt = dt.datetime(2020, 6, 15, 0, 0, 0)  # Midnight
    end_dt = dt.datetime(2023, 9, 22, 0, 0, 0)    # Midnight
    
    # Convert to midnight representations
    time_formats = {
        "date": start_dt.date(),
        "str_date": start_dt.strftime("%Y-%m-%d"),
    }
    
    end_time_formats = {
        "date": end_dt.date(),
        "str_date": end_dt.strftime("%Y-%m-%d"),
    }
    
    start_input = time_formats[input_type]
    end_input = end_time_formats[input_type]
    
    # Act: Create Age object
    age = Age(start_input, end_input)
    
    # Assert: Results should be identical to reference midnight datetime Age
    reference_age = Age(start_dt, end_dt)
    
    assert age.days == approx(reference_age.days, rel=1e-10), f"Days differ for {input_type}"
    assert age.seconds == reference_age.seconds, f"Seconds differ for {input_type}"
    assert age.years_precise == approx(reference_age.years_precise, rel=1e-10), f"Years precise differ for {input_type}"
    assert age.months_precise == approx(reference_age.months_precise, rel=1e-10), f"Months precise differ for {input_type}"


def test_age_datetime_vs_date_different_results() -> None:
    """
    Test that datetime with time components produces different results than date (which loses time).
    """
    # Arrange
    start_dt = dt.datetime(2020, 6, 15, 14, 30, 45)  # With time
    end_dt = dt.datetime(2023, 9, 22, 9, 15, 30)     # With time
    
    start_date = start_dt.date()  # Loses time -> midnight
    end_date = end_dt.date()      # Loses time -> midnight
    
    # Act
    age_datetime = Age(start_dt, end_dt)
    age_date = Age(start_date, end_date)
    
    # Assert: Should be different (datetime loses time information)
    assert age_datetime.days != age_date.days, "Datetime and date should produce different results"
    assert abs(age_datetime.days - age_date.days) > 0.1, "Difference should be significant"


# ---------- Biz Class Tests ----------

def test_biz_business_day_detection():
    """Test business day detection with holidays and weekends."""
    # Standard policy: Mon-Fri workdays, no holidays
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    
    # Monday (business day)
    chrono = Chrono(target_dt=dt.datetime(2024, 1, 1), policy=policy)  # Monday
    assert chrono.biz.is_business_day is True
    assert chrono.biz.is_workday is True
    assert chrono.biz.holiday is False
    
    # Saturday (weekend, not business day)
    chrono_sat = Chrono(target_dt=dt.datetime(2024, 1, 6), policy=policy)  # Saturday
    assert chrono_sat.biz.is_business_day is False
    assert chrono_sat.biz.is_workday is False
    assert chrono_sat.biz.holiday is False
    
    # Holiday policy
    holiday_policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays={"2024-01-01"})
    chrono_hol = Chrono(target_dt=dt.datetime(2024, 1, 1), policy=holiday_policy)  # Monday but holiday
    assert chrono_hol.biz.is_business_day is False
    assert chrono_hol.biz.is_workday is True  # Still a workday per policy
    assert chrono_hol.biz.holiday is True


def test_biz_fiscal_period_boundaries():
    """Test fiscal period start/end dates."""
    # April fiscal year start
    policy = BizPolicy(fiscal_year_start_month=4)
    
    # March 31 (end of Q4/fiscal year)
    chrono = Chrono(target_dt=dt.datetime(2024, 3, 31), policy=policy)
    assert chrono.biz.fiscal_year == 2023
    assert chrono.biz.fiscal_quarter == 4
    
    # April 1 (start of Q1/new fiscal year)
    chrono_apr = Chrono(target_dt=dt.datetime(2024, 4, 1), policy=policy)
    assert chrono_apr.biz.fiscal_year == 2024
    assert chrono_apr.biz.fiscal_quarter == 1
    
    # July 1 (Q2)
    chrono_jul = Chrono(target_dt=dt.datetime(2024, 7, 1), policy=policy)
    assert chrono_jul.biz.fiscal_year == 2024
    assert chrono_jul.biz.fiscal_quarter == 2
    
    # October 1 (Q3)
    chrono_oct = Chrono(target_dt=dt.datetime(2024, 10, 1), policy=policy)
    assert chrono_oct.biz.fiscal_year == 2024
    assert chrono_oct.biz.fiscal_quarter == 3
    
    # January 1 (Q4 of next fiscal year)
    chrono_jan = Chrono(target_dt=dt.datetime(2024, 1, 1), policy=policy)
    assert chrono_jan.biz.fiscal_year == 2023
    assert chrono_jan.biz.fiscal_quarter == 4


def test_biz_business_day_arithmetic():
    """Test business day range membership."""
    # Standard policy: Mon-Fri workdays, no holidays
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    
    # Reference: Wednesday, Jan 3, 2024
    ref_time = dt.datetime(2024, 1, 3)  # Wednesday
    
    # Target: Monday, Jan 1 (2 business days before ref)
    chrono_past = Chrono(target_dt=dt.datetime(2024, 1, 1), ref_dt=ref_time, policy=policy)
    assert chrono_past.biz.biz_day.in_(-2)  # Exactly 2 business days before
    
    # Target: Friday, Jan 5 (2 business days after ref)
    chrono_future = Chrono(target_dt=dt.datetime(2024, 1, 5), ref_dt=ref_time, policy=policy)
    assert chrono_future.biz.biz_day.in_(2)  # Exactly 2 business days after
    
    # Target: Saturday, Jan 6 (not a business day)
    chrono_weekend = Chrono(target_dt=dt.datetime(2024, 1, 6), ref_dt=ref_time, policy=policy)
    assert chrono_weekend.biz.biz_day.in_(-10, 10) is False  # Not a business day
    
    # Working days (ignore holidays)
    assert chrono_past.biz.work_day.in_(-2)  # Monday is a workday
    assert chrono_weekend.biz.work_day.in_(-10, 10) is False  # Saturday is not a workday


def test_biz_business_days_calculation():
    """Test fractional business days calculation."""
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays={"2024-01-01"})
    
    # Monday 9 AM to Tuesday 5 PM (standard business hours)
    start = dt.datetime(2024, 1, 2, 9, 0)  # Monday 9 AM
    end = dt.datetime(2024, 1, 3, 17, 0)   # Tuesday 5 PM
    chrono = Chrono(target_dt=start, ref_dt=end, policy=policy)
    
    # Should be 2 full business days
    assert chrono.biz.business_days == approx(2.0)
    
    # Working days (ignore holidays)
    assert chrono.biz.working_days == approx(2.0)
    
    # Partial day: Monday 9 AM to Monday 1 PM (4 hours = 0.5 business day)
    partial_start = dt.datetime(2024, 1, 2, 9, 0)   # Monday 9 AM
    partial_end = dt.datetime(2024, 1, 2, 13, 0)    # Monday 1 PM
    chrono_partial = Chrono(target_dt=partial_start, ref_dt=partial_end, policy=policy)
    assert chrono_partial.biz.business_days == approx(0.5)


# ---------- Chrono Class Integration Tests ----------

def test_chrono_property_integration():
    """Test that Chrono properties work together correctly."""
    target = dt.datetime(2024, 1, 1, 12, 0, 0)  # Monday
    ref = dt.datetime(2024, 1, 5, 12, 0, 0)     # Friday (same week)
    
    chrono = Chrono(target_dt=target, ref_dt=ref)
    
    # Age should show about 4 days
    assert chrono.age.days == approx(4.0)
    
    # Cal should show within same week
    assert chrono.cal.week.in_(0)  # Same week
    assert chrono.cal.day.in_(-4)  # Exactly 4 days ago
    
    # Biz should show business days (assuming standard policy)
    assert chrono.biz.business_days == approx(4.0)  # Mon-Thu-Fri
    assert chrono.biz.working_days == approx(4.0)  # Same as business days here
    
    # Fiscal properties
    assert chrono.biz.fiscal_year == 2024  # January 2024
    assert chrono.biz.fiscal_quarter == 1  # Q1 for standard Jan fiscal year start


def test_chrono_edge_cases():
    """Test Chrono with edge case dates."""
    now = dt.datetime.now()
    
    # Very old date
    old_date = dt.datetime(1900, 1, 1)
    chrono_old = Chrono(target_dt=old_date)
    assert chrono_old.age.days > 40000  # Should be many days (positive duration)
    assert chrono_old.age.years > 120   # Should be over 120 years
    
    # Future date  
    future_date = dt.datetime(2100, 1, 1)
    chrono_future = Chrono(target_dt=future_date)
    assert chrono_future.age.days < -20000  # Should be negative (future from now)
    assert chrono_future.age.years < -70    # Should be negative
    
    # Same instant (should be zero)
    chrono_same = Chrono(target_dt=now, ref_dt=now)
    assert chrono_same.age.seconds == 0
    assert chrono_same.age.days == 0
    
    # Very close times (fractional seconds)
    close_time = now + dt.timedelta(microseconds=500000)  # 0.5 seconds later
    chrono_close = Chrono(target_dt=now, ref_dt=close_time)
    assert chrono_close.age.seconds == pytest.approx(0.5, abs=0.01)


def test_chrono_fiscal_shortcuts():
    """Test Chrono fiscal shortcut properties."""
    # Standard fiscal year (Jan start)
    policy = BizPolicy(fiscal_year_start_month=1)
    ref_time = dt.datetime(2024, 6, 15)  # June 15, 2024
    
    # Target in same fiscal year
    chrono_same = Chrono(target_dt=dt.datetime(2024, 3, 1), ref_dt=ref_time, policy=policy)
    assert chrono_same.biz.is_this_fiscal_year is True
    assert chrono_same.biz.is_last_fiscal_year is False
    assert chrono_same.biz.is_next_fiscal_year is False
    
    # Target in last fiscal year
    chrono_last = Chrono(target_dt=dt.datetime(2023, 12, 1), ref_dt=ref_time, policy=policy)
    assert chrono_last.biz.is_this_fiscal_year is False
    assert chrono_last.biz.is_last_fiscal_year is True
    assert chrono_last.biz.is_next_fiscal_year is False
    
    # Target in next fiscal year
    chrono_next = Chrono(target_dt=dt.datetime(2025, 2, 1), ref_dt=ref_time, policy=policy)
    assert chrono_next.biz.is_this_fiscal_year is False
    assert chrono_next.biz.is_last_fiscal_year is False
    assert chrono_next.biz.is_next_fiscal_year is True


def test_chrono_business_day_shortcuts():
    """Test Chrono business day shortcut properties."""
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    ref_time = dt.datetime(2024, 1, 3)  # Wednesday
    
    # Same business day
    chrono_same = Chrono(target_dt=dt.datetime(2024, 1, 3), ref_dt=ref_time, policy=policy)
    assert chrono_same.biz.is_business_this_day is True
    assert chrono_same.biz.is_business_last_day is False
    assert chrono_same.biz.is_business_next_day is False
    
    # Previous business day (Tuesday)
    chrono_last = Chrono(target_dt=dt.datetime(2024, 1, 2), ref_dt=ref_time, policy=policy)
    assert chrono_last.biz.is_business_this_day is False
    assert chrono_last.biz.is_business_last_day is True
    assert chrono_last.biz.is_business_next_day is False
    
    # Next business day (Thursday)
    chrono_next = Chrono(target_dt=dt.datetime(2024, 1, 4), ref_dt=ref_time, policy=policy)
    assert chrono_next.biz.is_business_this_day is False
    assert chrono_next.biz.is_business_last_day is False
    assert chrono_next.biz.is_business_next_day is True
    
    # Weekend (not a business day)
    chrono_weekend = Chrono(target_dt=dt.datetime(2024, 1, 6), ref_dt=ref_time, policy=policy)
    assert chrono_weekend.biz.is_business_this_day is False
    assert chrono_weekend.biz.is_business_last_day is False
    assert chrono_weekend.biz.is_business_next_day is False