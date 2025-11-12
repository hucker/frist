import datetime as dt
import pytest
from frist._cal import Cal

def test_in_workdays_start_greater_than_end():
    """AAA: Arrange, Act, Assert
    Arrange: Create Cal and call in_workdays with start > end
    Act & Assert: ValueError is raised
    """
    cal = Cal(dt.datetime(2024, 5, 6), dt.datetime(2024, 5, 6))
    with pytest.raises(ValueError, match="start.*must not be greater than end"):
        cal.in_workdays(2, 1)

def test_in_workdays_target_is_weekend():
    """AAA: Arrange, Act, Assert
    Arrange: Target date is a Saturday
    Act: Call in_workdays
    Assert: Returns False
    """
    # Saturday May 11, 2024
    cal = Cal(dt.datetime(2024, 5, 11), dt.datetime(2024, 5, 6))
    result = cal.in_workdays(0, 4)
    assert result is False, "Should return False for weekend target date"

def test_in_workdays_target_is_holiday():
    """AAA: Arrange, Act, Assert
    Arrange: Target date is a holiday
    Act: Call in_workdays
    Assert: Returns False
    """
    # Wednesday May 8, 2024, holiday
    cal = Cal(dt.datetime(2024, 5, 8), dt.datetime(2024, 5, 6), holidays={"2024-05-08"})
    result = cal.in_workdays(0, 2)
    assert result is False, "Should return False for holiday target date"
