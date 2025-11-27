"""
Unit tests for BizPolicy exception handling.

Verifies that BizPolicy methods raise TypeError for invalid input types.
"""
import datetime as dt
import pytest
from frist._cal_policy import BizPolicy

def make_policy():
    return BizPolicy(holidays={"2025-11-13"})

def test_is_weekend_typeerror() -> None:
    """
    Test is_weekend raises TypeError for invalid input types.
    """
    policy = make_policy()
    with pytest.raises(TypeError, match="is_weekend expects int, date, or datetime"):
        policy.is_weekend("not-a-date") #type: ignore # Intentional wrong type for test
    with pytest.raises(TypeError, match="is_weekend expects int, date, or datetime"):
        policy.is_weekend([1, 2, 3]) #type: ignore # Intentional wrong type for test

def test_is_workday_typeerror() -> None:
    """
    Test is_workday raises TypeError for invalid input types.
    """
    policy = make_policy()
    with pytest.raises(TypeError, match="is_workday expects int, date, or datetime"):
        policy.is_workday("not-a-date")
    with pytest.raises(TypeError, match="is_workday expects int, date, or datetime"):
        policy.is_workday([1, 2, 3])

def test_is_holiday_typeerror() -> None:
    """
    Test is_holiday raises TypeError for invalid input types.
    """
    policy = make_policy()
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday(12345)
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday(["2025-11-13"])
