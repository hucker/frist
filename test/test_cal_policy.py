"""
Unit tests for CalendarPolicy.is_holiday method.

Tests string, date, and datetime inputs, as well as error handling for invalid types.
Follows AAA pattern and includes assert messages for codestyle compliance.
"""
import datetime as dt
import pytest
from frist._cal_policy import CalendarPolicy

def test_is_holiday_str():
    """
    Test is_holiday with string input.
    """
    # Arrange
    policy = CalendarPolicy(holidays={"2025-11-13", "2025-12-25"})
    # Act & Assert
    assert policy.is_holiday("2025-11-13") is True, "is_holiday('2025-11-13') should be True"
    assert policy.is_holiday("2025-12-25") is True, "is_holiday('2025-12-25') should be True"
    assert policy.is_holiday("2025-01-01") is False, "is_holiday('2025-01-01') should be False"

def test_is_holiday_date():
    """
    Test is_holiday with date input.
    """
    # Arrange
    policy = CalendarPolicy(holidays={"2025-11-13"})
    date = dt.date(2025, 11, 13)
    # Act & Assert
    assert policy.is_holiday(date) is True, f"is_holiday({date}) should be True"
    assert policy.is_holiday(dt.date(2025, 1, 1)) is False, "is_holiday(2025-01-01) should be False"

def test_is_holiday_datetime():
    """
    Test is_holiday with datetime input.
    """
    # Arrange
    policy = CalendarPolicy(holidays={"2025-11-13"})
    dt_obj = dt.datetime(2025, 11, 13, 10, 0)
    # Act & Assert
    assert policy.is_holiday(dt_obj) is True, f"is_holiday({dt_obj}) should be True"
    assert policy.is_holiday(dt.datetime(2025, 1, 1, 0, 0)) is False, "is_holiday(2025-01-01 00:00) should be False"

def test_is_holiday_invalid_type():
    """
    Test is_holiday raises TypeError for invalid input types.
    """
    # Arrange
    policy = CalendarPolicy()
    # Act & Assert
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday(12345)  #type: ignore # Intentional wrong type for test
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday(["2025-11-13"]) #type: ignore # Intentional wrong type for test

def test_calendar_policy_invalid_workdays_type() -> None:
    """
    Test that CalendarPolicy raises TypeError if workdays is not a list.
    """
    with pytest.raises(TypeError, match="workdays must be a list"):
        CalendarPolicy(workdays=(0, 1, 2, 3, 4))  # tuple instead of list
    with pytest.raises(TypeError, match="workdays must be a list"):
        CalendarPolicy(workdays="01234")  # string instead of list
    with pytest.raises(TypeError, match="workdays must be a list"):
        CalendarPolicy(workdays=None)  # None instead of list

def test_calendar_policy_invalid_holidays_type() -> None:
    """
    Test that CalendarPolicy raises TypeError if holidays is not a set.
    """
    with pytest.raises(TypeError, match="holidays must be a set"):
        CalendarPolicy(holidays=["2025-11-13"])  # list instead of set
    with pytest.raises(TypeError, match="holidays must be a set"):
        CalendarPolicy(holidays="2025-11-13")  # string instead of set
    with pytest.raises(TypeError, match="holidays must be a set"):
        CalendarPolicy(holidays=None)  # None instead of set

def test_calendar_policy_invalid_fiscal_year_start_month() -> None:
    """
    Test that CalendarPolicy raises ValueError for invalid fiscal_year_start_month (coverage for __post_init__ line 31).
    """
    import pytest
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=0)
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=13)
def test_fiscal_year_start_month_validation() -> None:
    """
    Test CalendarPolicy raises ValueError for invalid fiscal_year_start_month.
    """
    import pytest
    # Invalid: 0
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=0)
    # Invalid: 13
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=13)
