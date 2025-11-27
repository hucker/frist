"""
Unit tests for BizPolicy exception handling in __post_init__ and methods.
"""
import datetime as dt
import pytest
from frist._cal_policy import BizPolicy

def test_invalid_fiscal_year_start_month_exception() -> None:
    """
    Test that invalid fiscal_year_start_month raises ValueError.
    """
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        BizPolicy(fiscal_year_start_month=0)
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        BizPolicy(fiscal_year_start_month=13)

def test_invalid_workdays_length_exception() -> None:
    """
    Test that workdays longer than 7 raises ValueError.
    """
    with pytest.raises(ValueError, match="workdays must have 0 to 7 values"):
        BizPolicy(workdays=list(range(8)))

def test_invalid_workdays_value_exception() -> None:
    """
    Test that workdays with values outside 0..6 raises ValueError.
    """
    with pytest.raises(ValueError, match="workdays must contain only integers 0..6"):
        BizPolicy(workdays=[-1, 0, 1])
    with pytest.raises(ValueError, match="workdays must contain only integers 0..6"):
        BizPolicy(workdays=[0, 1, 2, 3, 4, 5, 7])

def test_is_holiday_typeerror() -> None:
    """
    Test is_holiday raises TypeError for invalid input types.
    """
    policy = BizPolicy()
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday(12345)
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday(["2025-11-13"])

def test_is_workday_typeerror() -> None:
    """
    Test is_workday raises TypeError for invalid input types.
    """
    policy = BizPolicy()
    with pytest.raises(TypeError, match="is_workday expects int, date, or datetime"):
        policy.is_workday("not-a-date")
    with pytest.raises(TypeError, match="is_workday expects int, date, or datetime"):
        policy.is_workday([1, 2, 3])

def test_is_weekend_typeerror() -> None:
    """
    Test is_weekend raises TypeError for invalid input types.
    """
    policy = BizPolicy()
    with pytest.raises(TypeError, match="is_weekend expects int, date, or datetime"):
        policy.is_weekend("not-a-date")
    with pytest.raises(TypeError, match="is_weekend expects int, date, or datetime"):
        policy.is_weekend([1, 2, 3])
