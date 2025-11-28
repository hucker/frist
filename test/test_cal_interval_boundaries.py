"""
Boundary tests for Cal interval methods.
Verifies half-open interval semantics: start <= value < end for each time scale.
Follows Frist CODESTYLE.md: AAA comments, one test per time scale.
"""
import datetime as dt
import pytest

from frist import Chrono,Cal,BizPolicy


# Local fixture for Cal instance

@pytest.fixture
def cal_factory() -> Cal:
    """
    Fixture that returns a Cal instance for interval boundary tests.
    Uses a fixed ref_dt and value for consistency.
    """
    ref_dt: dt.datetime = dt.datetime(2025, 1, 1, 0, 0, 0)
    value: dt.datetime = dt.datetime(2025, 1, 1, 0, 0, 0)
    z: Chrono = Chrono(target_time=value, reference_time=ref_dt)
    return z.cal

@pytest.fixture
def cal_policy() -> BizPolicy:
    """
    Fixture that returns a BizPolicy instance for interval boundary tests.
    Uses default settings but adds fiscal year starting in April.
    """
    return BizPolicy(fiscal_year_start_month=4)


def test_minute_interval_half_open():
    """Test minute interval is half-open: start <= value < end."""
    # Arrange
    ref_dt: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    value: dt.datetime = dt.datetime(2024, 1, 1, 12, 1, 0)
    cal: Cal = Chrono(target_time=value, reference_time=ref_dt).cal
    # Act
    in_current = cal.min.in_(0)
    in_next = cal.min.in_(1)
    # Assert
    assert in_current is False, "Value at end of minute should not be in current interval"
    assert in_next is True, "Value at start of next minute should be in next interval"


def test_hour_interval_half_open():
    """Test hour interval is half-open: start <= value < end."""
    # Arrange
    ref_dt: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    value: dt.datetime = ref_dt.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=1)
    z: Chrono = Chrono(target_time=value, reference_time=ref_dt)
    cal: Cal = z.cal
    # Act
    in_current = cal.hr.in_(0)
    in_next = cal.hr.in_(1)
    # Assert
    assert in_current is False, "Value at end of hour should not be in current interval"
    assert in_next is True, "Value at start of next hour should be in next interval"


def test_quarter_interval_half_open():
    """Test quarter interval is half-open: start <= value < end."""
    # Arrange
    ref_dt: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    value: dt.datetime = ref_dt.replace(month=4, day=1, hour=0, minute=0, second=0, microsecond=0)  # Q2 start
    
    z: Chrono = Chrono(target_time=value, reference_time=ref_dt)
    cal: Cal = z.cal
    # Act
    in_current = cal.qtr.in_(0)
    in_next = cal.qtr.in_(1)
    # Assert
    assert in_current is False, "Value at end of quarter should not be in current interval"
    assert in_next is True, "Value at start of next quarter should be in next interval"



def test_in_xxx_start_greater_than_end(cal_factory:Cal):
    """Test that in_xxx methods raise ValueError when start > end."""
    cal:Cal = cal_factory
    # All should raise ValueError when start > end
    with pytest.raises(ValueError):
        cal.min.in_(1, 0)
    with pytest.raises(ValueError):
        cal.hr.in_(1, 0)
    with pytest.raises(ValueError):
        cal.day.in_(1, 0)
    with pytest.raises(ValueError):
        cal.mon.in_(1, 0)
    with pytest.raises(ValueError):
        cal.qtr.in_(1, 0)
    with pytest.raises(ValueError):
        cal.year.in_(1, 0)
    with pytest.raises(ValueError):
        cal.wk.in_(1, 0)


def test_year_interval_half_open():
    """Test year interval is half-open: start <= value < end."""
    # Arrange
    ref_dt:dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    value:dt.datetime = dt.datetime(2025, 1, 1, 0, 0, 0)  # First moment of next year
    z:Chrono = Chrono(target_time=value, reference_time=ref_dt)
    cal:Cal = z.cal
    # Act
    in_current:bool = cal.year.in_(0)
    in_next:bool = cal.year.in_(1)
    # Assert
    assert in_current is False, "Value at start of next year should not be in current interval"
    assert in_next is True, "Value at start of next year should be in next interval"
