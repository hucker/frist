"""Targeted tests to cover small alternate branches in `src/frist/_cal.py`.

These include:
- invalid inputs to `normalize_weekday` that raise ValueError
- constructing `Cal` with numeric timestamps and invalid types raising TypeError
- verifying `is_*` shortcut properties delegate to `in_*` methods
"""
import datetime as dt
import pytest

from frist._cal import Cal
from frist._util import normalize_weekday

def test_normalize_weekday_invalid_raises() -> None:
    """Test that normalize_weekday raises ValueError for invalid day specifications."""
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("not-a-day")


def test_cal_init_numeric_and_typeerror() -> None:
    """Test Cal initialization with numeric timestamps and invalid types."""
    # Arrange
    ref = dt.datetime(2025, 3, 15, 12, 0, 0)
    
    # Act & Assert
    # numeric timestamp (int)
    ts = int(ref.timestamp())
    c = Cal(target_dt=ts, ref_dt=ts)
    assert isinstance(c.target_dt, dt.datetime), "target_dt should be converted to datetime"
    assert isinstance(c.ref_dt, dt.datetime), "ref_dt should be converted to datetime"

    # invalid target_dt type
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal(target_dt="bad", ref_dt=ref)

    # invalid ref_dt type
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal(target_dt=ref, ref_dt="bad")


def test_cal_shortcut_properties_delegate_to_methods() -> None:
    """Test that Cal shortcut properties delegate to in_() methods correctly."""
    # Arrange
    ref = dt.datetime(2025, 4, 10, 12, 0, 0)
    
    # Act
    # choose a target equal to ref for 'this' shortcuts
    c = Cal(target_dt=ref, ref_dt=ref)

    # Assert
    # Golden assertions for shortcuts (explicit expectations, not parity checks)
    assert c.is_today is True, "Target should be today when equal to reference"
    assert c.is_this_week is True, "Target should be this week when equal to reference"
    assert c.is_this_month is True, "Target should be this month when equal to reference"
    assert c.is_this_quarter is True
    assert c.is_this_year is True

    # last/next variants
    assert c.is_last_week is False
    assert c.is_next_week is False
    assert c.is_last_month is False
    assert c.is_next_month is False
    assert c.is_last_quarter is False
    assert c.is_next_quarter is False
    assert c.is_last_year is False
    assert c.is_next_year is False

    # explicit yesterday/tomorrow checks using golden expectations
    ref2 = dt.datetime(2025, 4, 11, 12, 0, 0)
    cal_y = Cal(target_dt=ref2 - dt.timedelta(days=1), ref_dt=ref2)
    cal_t = Cal(target_dt=ref2 + dt.timedelta(days=1), ref_dt=ref2)

    assert cal_y.is_yesterday is True
    assert cal_t.is_tomorrow is True


def test_normalize_weekday_pandas_prefix_invalid() -> None:
    """Test that normalize_weekday raises ValueError for invalid pandas-style day codes."""
    # ensure pandas-style prefix branch is exercised and raises for unknown code
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("w-xyz")
