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
        CalendarPolicy(workdays=(0, 1, 2, 3, 4))  # type: ignore # should be bad type
    with pytest.raises(TypeError, match="workdays must be a list"):
        CalendarPolicy(workdays="01234")  # type:ignore # should be bad type
    with pytest.raises(TypeError, match="workdays must be a list"):
        CalendarPolicy(workdays=None)  # type:ignore # should be bad type

def test_calendar_policy_invalid_holidays_type() -> None:
    """
    Test that CalendarPolicy raises TypeError if holidays is not a set.
    """
    with pytest.raises(TypeError, match="holidays must be a set"):
        CalendarPolicy(holidays=["2025-11-13"])  # type:ignore # should be bad type
    with pytest.raises(TypeError, match="holidays must be a set"):
        CalendarPolicy(holidays="2025-11-13")  # type:ignore # should be bad type
    with pytest.raises(TypeError, match="holidays must be a set"):
        CalendarPolicy(holidays=None)  # type:ignore # should be bad type

def test_calendar_policy_invalid_fiscal_year_start_month() -> None:
    """
    Test that CalendarPolicy raises ValueError for invalid fiscal_year_start_month (coverage for __post_init__ line 31).
    """
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=0)
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=13)

def test_fiscal_year_start_month_validation() -> None:
    """
    Test CalendarPolicy raises ValueError for invalid fiscal_year_start_month.
    """
    # Invalid: 0
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=0)
    # Invalid: 13
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        CalendarPolicy(fiscal_year_start_month=13)

@pytest.mark.parametrize("good_date", [
    "1900-01-01",
    "1999-12-31",
    "2025-11-13",
    "2099-12-31",
])
def test_valid_date_str_true(good_date:str):
    policy = CalendarPolicy()
    assert policy.valid_date_str(good_date) is True, f"valid_date_str('{good_date}') should be True"

def test_is_business_day_invalid_type():
    """
    Test is_business_day raises TypeError for invalid input types.
    """
    policy = CalendarPolicy()
    with pytest.raises(TypeError, match="is_business_day expects date, or datetime"):
        policy.is_business_day(12345)  # type: ignore
    with pytest.raises(TypeError, match="is_business_day expects date, or datetime"):
        policy.is_business_day("2025-11-13")  # type: ignore
    with pytest.raises(TypeError, match="is_business_day expects date, or datetime"):
        policy.is_business_day([dt.date(2025, 11, 13)])  # type: ignore

@pytest.mark.parametrize("bad_str", [
    "2024-02-30",  # impossible date
    "2024-13-01",  # invalid month
    "2024-00-10",  # invalid month
    "2024-8-8",    # invalid format
    "1899-01-01",  # year out of range
    "2100-01-01",  # year out of range
])
def test_is_holiday_valueerror_for_bad_str(bad_str):
    policy = CalendarPolicy()
    with pytest.raises(ValueError):
        policy.is_holiday(bad_str)

def test_is_business_day_typeerror():
    policy = CalendarPolicy()
    with pytest.raises(TypeError, match="is_business_day expects date, or datetime"):
        policy.is_business_day(42)  # int, not date/datetime
    with pytest.raises(TypeError, match="is_business_day expects date, or datetime"):
        policy.is_business_day("2025-11-13")   # type: ignore # Intentional wrong type for test

def test_is_holiday_typeerror():
    policy = CalendarPolicy()
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday(42)  # int, not str/date/datetime
    with pytest.raises(TypeError, match="is_holiday expects str"):
        policy.is_holiday([2025, 11, 13])  # type: ignore # Intentional wrong type for test

def test_is_business_day_typeerror_none():
    policy = CalendarPolicy()
    with pytest.raises(TypeError, match="is_business_day expects date, or datetime"):
        policy.is_business_day(None)   # type: ignore # Intentional wrong type for test

def test_is_business_day_true_false():
    policy = CalendarPolicy(holidays={"2025-11-13"})
    # Workday, not holiday
    date = dt.date(2025, 11, 12)  # Wednesday
    assert policy.is_business_day(date) is True, "Should be business day (workday, not holiday)"
    # Holiday
    date_holiday = dt.date(2025, 11, 13)  # Thursday
    assert policy.is_business_day(date_holiday) is False, "Should not be business day (holiday)"
    # Weekend
    date_weekend = dt.date(2025, 11, 15)  # Saturday
    assert policy.is_business_day(date_weekend) is False, "Should not be business day (weekend)"
    # Workday, not holiday, as datetime
    dt_obj = dt.datetime(2025, 11, 12, 10, 0)
    assert policy.is_business_day(dt_obj) is True, "Should be business day (datetime)"
    # Holiday, as datetime
    dt_obj_holiday = dt.datetime(2025, 11, 13, 10, 0)
    assert policy.is_business_day(dt_obj_holiday) is False, "Should not be business day (holiday, datetime)"
    # Weekend, as datetime
    dt_obj_weekend = dt.datetime(2025, 11, 15, 10, 0)
    assert policy.is_business_day(dt_obj_weekend) is False, "Should not be business day (weekend, datetime)"

@pytest.mark.parametrize("bad_type", [
    12345,
    None,
    "2025-11-13",
    [dt.date(2025, 11, 13)],
    object(),
])
def test_is_business_day_typeerror_for_bad_types(bad_type):
    policy = CalendarPolicy()
    with pytest.raises(TypeError):
        policy.is_business_day(bad_type)  # type: ignore # Intentional wrong type for test

@pytest.mark.parametrize("bad_type", [12345, None, ["2025-11-13"], {"date": "2025-11-13"}, object()])
def test_valid_date_str_non_string(bad_type):
    policy = CalendarPolicy()
    assert policy.valid_date_str(bad_type) is False  # type: ignore # Intentional wrong type for test