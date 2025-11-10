"""
Boundary tests for Cal interval methods.
Verifies half-open interval semantics: start <= value < end for each time scale.
Follows Frist CODESTYLE.md: AAA comments, one test per time scale.
"""
import datetime as dt
import pytest

from frist import Frist
from frist._cal import Cal


# Local fixture for Cal instance

@pytest.fixture
def cal_factory() -> Cal:
    """
    Fixture that returns a Cal instance for interval boundary tests.
    Uses a fixed base_time and value for consistency.
    """
    base_time: dt.datetime = dt.datetime(2025, 1, 1, 0, 0, 0)
    value: dt.datetime = dt.datetime(2025, 1, 1, 0, 0, 0)
    z: Frist = Frist(target_time=value, reference_time=base_time)
    return z.cal


def test_minute_interval_half_open():
    """Test minute interval is half-open: start <= value < end."""
    # Arrange
    base_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    value = base_time.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)
    z = Frist(target_time=value, reference_time=base_time)
    cal = z.cal
    # Act
    in_current = cal.in_minutes(0)
    in_next = cal.in_minutes(1)
    # Assert
    assert in_current is False, "Value at end of minute should not be in current interval"
    assert in_next is True, "Value at start of next minute should be in next interval"

def test_hour_interval_half_open():
    """Test hour interval is half-open: start <= value < end."""
    # Arrange
    base_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    value = base_time.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=1)
    z = Frist(target_time=value, reference_time=base_time)
    cal = z.cal
    # Act
    in_current = cal.in_hours(0)
    in_next = cal.in_hours(1)
    # Assert
    assert in_current is False, "Value at end of hour should not be in current interval"
    assert in_next is True, "Value at start of next hour should be in next interval"

def test_quarter_interval_half_open():
    """Test quarter interval is half-open: start <= value < end."""
    # Arrange
    base_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    value = base_time.replace(month=4, day=1, hour=0, minute=0, second=0, microsecond=0)  # Q2 start
    z = Frist(target_time=value, reference_time=base_time)
    cal = z.cal
    # Act
    in_current = cal.in_quarters(0)
    in_next = cal.in_quarters(1)
    # Assert
    assert in_current is False, "Value at end of quarter should not be in current interval"
    assert in_next is True, "Value at start of next quarter should be in next interval"

def test_fiscal_quarter_interval_half_open():
    """Test fiscal quarter interval is half-open: start <= value < end (custom fiscal year start)."""
    # Arrange
    fy_start_month = 4
    base_time = dt.datetime(2024, 6, 30, 12, 0, 0)  # Last day of Q1
    value = dt.datetime(2024, 7, 1, 0, 0, 0)  # First day of Q2
    z = Frist(target_time=value, reference_time=base_time, fy_start_month=fy_start_month)
    cal = z.cal
    # Act
    in_prev = cal.fiscal_quarter == 1
    in_new = cal.fiscal_quarter == 2
    # Assert
    assert in_prev is False, "Value at start of fiscal quarter should not be in previous interval"
    assert in_new is True, "Value at start of new fiscal quarter should be in new interval"

def test_fiscal_year_interval_half_open():
    """Test fiscal year interval is half-open: start <= value < end (custom fiscal year start)."""
    # Arrange
    fy_start_month = 4
    base_time = dt.datetime(2024, 3, 31, 12, 0, 0)  # Last day before fiscal year starts
    value = dt.datetime(2024, 4, 1, 0, 0, 0)  # First day of new fiscal year
    z = Frist(target_time=value, reference_time=base_time, fy_start_month=fy_start_month)
    cal = z.cal
    # Act
    in_prev = cal.fiscal_year == 2023
    in_new = cal.fiscal_year == 2024
    # Assert
    assert in_prev is False, "Value at start of fiscal year should not be in previous interval"
    assert in_new is True, "Value at start of new fiscal year should be in new interval"

def test_in_fiscal_quarters_half_open():
    """Test in_fiscal_quarters is half-open: start <= value < end (custom fiscal year start)."""
    # Arrange
    fy_start_month = 4
    base_time = dt.datetime(2024, 6, 30, 12, 0, 0)  # Last day of Q1
    value = dt.datetime(2024, 7, 1, 0, 0, 0)  # First day of Q2
    z = Frist(target_time=value, reference_time=base_time, fy_start_month=fy_start_month)
    cal = z.cal
    # Act
    in_current = cal.in_fiscal_quarters(0)
    in_next = cal.in_fiscal_quarters(1)
    # Assert
    assert in_current is False, "Value at start of next fiscal quarter should not be in current interval"
    assert in_next is True, "Value at start of next fiscal quarter should be in next interval"

def test_in_fiscal_years_half_open():
    """Test in_fiscal_years is half-open: start <= value < end (custom fiscal year start)."""
    # Arrange
    fy_start_month = 4
    base_time = dt.datetime(2024, 3, 31, 12, 0, 0)  # Last day before fiscal year starts
    value = dt.datetime(2024, 4, 1, 0, 0, 0)  # First day of new fiscal year
    z = Frist(target_time=value, reference_time=base_time, fy_start_month=fy_start_month)
    cal = z.cal
    # Act
    in_current = cal.in_fiscal_years(0)
    in_next = cal.in_fiscal_years(1)
    # Assert
    assert in_current is False, "Value at start of next fiscal year should not be in current interval"
    assert in_next is True, "Value at start of next fiscal year should be in next interval"
def test_in_xxx_start_greater_than_end(cal_factory):
    cal = cal_factory
    # All should raise ValueError when start > end
    with pytest.raises(ValueError):
        cal.in_minutes(1, 0)
    with pytest.raises(ValueError):
        cal.in_hours(1, 0)
    with pytest.raises(ValueError):
        cal.in_days(1, 0)
    with pytest.raises(ValueError):
        cal.in_months(1, 0)
    with pytest.raises(ValueError):
        cal.in_quarters(1, 0)
    with pytest.raises(ValueError):
        cal.in_years(1, 0)
    with pytest.raises(ValueError):
        cal.in_weeks(1, 0)
    with pytest.raises(ValueError):
        cal.in_fiscal_quarters(1, 0)
    with pytest.raises(ValueError):
        cal.in_fiscal_years(1, 0)

def test_year_interval_half_open():
    """Test year interval is half-open: start <= value < end."""
    # Arrange
    base_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    value = dt.datetime(2025, 1, 1, 0, 0, 0)  # First moment of next year
    z = Frist(target_time=value, reference_time=base_time)
    cal = z.cal
    # Act
    in_current = cal.in_years(0)
    in_next = cal.in_years(1)
    # Assert
    assert in_current is False, "Value at start of next year should not be in current interval"
    assert in_next is True, "Value at start of next year should be in next interval"
