

"""
Tests for Cal.count_working_days static method.

Covers edge cases: basic range, holidays, weekends, all holidays, invalid range, single day workday, single day weekend, single day holiday.
"""

import datetime as dt
from frist._cal import Cal

def test_count_working_days_basic():
    """
    Test counting workdays in a normal week (Mon-Fri, no holidays).
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 6)  # Monday
    end: dt.date = dt.date(2024, 5, 10)   # Friday
    holidays: set[str] = set()
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 5, f"Expected 5 workdays (Mon-Fri), got {result}"

def test_count_working_days_with_holiday():
    """
    Test counting workdays in a week with a holiday (Wednesday).
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 6)  # Monday
    end: dt.date = dt.date(2024, 5, 10)   # Friday
    holidays: set[str] = {"2024-05-08"}  # Wednesday is a holiday
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 4, f"Expected 4 workdays (Wed is holiday), got {result}"

def test_count_working_days_weekend_included():
    """
    Test counting workdays when range includes a weekend (Fri-Mon).
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 10)  # Friday
    end: dt.date = dt.date(2024, 5, 13)    # Monday
    holidays: set[str] = set()
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 2, f"Expected 2 workdays (Fri, Mon), got {result}"

def test_count_working_days_all_holidays():
    """
    Test counting workdays when all days in range are holidays.
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 6)  # Monday
    end: dt.date = dt.date(2024, 5, 10)   # Friday
    holidays: set[str] = {"2024-05-06", "2024-05-07", "2024-05-08", "2024-05-09", "2024-05-10"}
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 0, f"Expected 0 workdays (all are holidays), got {result}"

def test_count_working_days_start_after_end():
    """
    Test counting workdays when start date is after end date (invalid range).
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 10)  # Friday
    end: dt.date = dt.date(2024, 5, 6)     # Monday
    holidays: set[str] = set()
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 0, f"Expected 0 workdays (start after end), got {result}"

def test_count_working_days_single_day_workday():
    """
    Test counting workdays for a single workday (Wednesday).
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 8)  # Wednesday
    end: dt.date = dt.date(2024, 5, 8)    # Wednesday
    holidays: set[str] = set()
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 1, f"Expected 1 workday (Wed), got {result}"

def test_count_working_days_single_day_weekend():
    """
    Test counting workdays for a single weekend day (Saturday).
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 11)  # Saturday
    end: dt.date = dt.date(2024, 5, 11)    # Saturday
    holidays: set[str] = set()
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 0, f"Expected 0 workdays (Sat is weekend), got {result}"

def test_count_working_days_single_day_holiday():
    """
    Test counting workdays for a single holiday (Wednesday).
    """
    # Arrange
    start: dt.date = dt.date(2024, 5, 8)  # Wednesday
    end: dt.date = dt.date(2024, 5, 8)    # Wednesday
    holidays: set[str] = {"2024-05-08"}
    # Act
    result = Cal.count_working_days(start, end, holidays)
    # Assert
    assert result == 0, f"Expected 0 workdays (Wed is holiday), got {result}"
