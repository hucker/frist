"""
Unit test for Age: verifies presence and type of cal_policy object.
"""
import datetime as dt
from frist._age import Age
from frist._cal_policy import CalendarPolicy

def test_age_default_calendar_policy() -> None:
    """
    Test that the default CalendarPolicy in Age uses Monday-Friday as workdays and no holidays.

    Expectation: The default CalendarPolicy should have workdays [0, 1, 2, 3, 4] (Monday-Friday) and an empty holidays set.
    """
    # Arrange
    age = Age(dt.datetime(2025, 1, 1), dt.datetime(2025, 11, 13))
    cal_policy = age.cal_policy
    # Assert
    assert cal_policy.workdays == [0, 1, 2, 3, 4], (
        f"Expected default workdays [0, 1, 2, 3, 4], got {cal_policy.workdays}"
    )
    assert cal_policy.holidays == set(), (
        f"Expected default holidays to be empty, got {cal_policy.holidays}"
    )

    # Call date functions to verify default behavior
    monday = dt.date(2025, 11, 10)  # Monday
    saturday = dt.date(2025, 11, 15)  # Saturday
    assert cal_policy.is_workday(monday) is True, "Monday should be a workday by default"
    assert cal_policy.is_workday(saturday) is False, "Saturday should not be a workday by default"
    assert cal_policy.is_weekend(monday) is False, "Monday should not be a weekend by default"
    assert cal_policy.is_weekend(saturday) is True, "Saturday should be a weekend by default"
    assert cal_policy.is_holiday(monday) is False, "No holidays should be set by default"

def test_age_has_calendar_policy() -> None:
    """
    Test that Age object has a calendar policy attribute and it is a CalendarPolicy instance.
    """
    # Arrange
    age = Age(dt.datetime(2025, 1, 1), dt.datetime(2025, 11, 13))
    # Act
    cal_policy = age.cal_policy
    # Assert
    assert isinstance(cal_policy, CalendarPolicy), f"Expected CalendarPolicy, got {type(cal_policy)}"

    # Test with custom CalendarPolicy
    custom_policy = CalendarPolicy(workdays=[1,2,3])
    age2 = Age(dt.datetime(2025, 1, 1), dt.datetime(2025, 11, 13), cal_policy=custom_policy)
    assert age2.cal_policy is custom_policy, "Custom CalendarPolicy should be used if provided"
