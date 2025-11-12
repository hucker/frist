import datetime as dt
from frist._cal import Cal

def test_in_workdays_start_equals_end():
    """AAA: Arrange, Act, Assert
    Arrange: start and end are the same, target is a workday
    Act: Call in_workdays
    Assert: Returns True if target is a workday, False otherwise
    """
    # Wednesday May 8, 2024 (workday)
    cal = Cal(dt.datetime(2024, 5, 8), dt.datetime(2024, 5, 8))
    result = cal.in_workdays(0, 0)
    assert result is True, "Should return True when target is a workday and start == end == 0"

    # Saturday May 11, 2024 (weekend)
    cal_weekend = Cal(dt.datetime(2024, 5, 11), dt.datetime(2024, 5, 11))
    result_weekend = cal_weekend.in_workdays(0, 0)
    assert result_weekend is False, "Should return False when target is a weekend and start == end == 0"

    # Wednesday May 8, 2024 (holiday)
    cal_holiday = Cal(dt.datetime(2024, 5, 8), dt.datetime(2024, 5, 8), holidays={"2024-05-08"})
    result_holiday = cal_holiday.in_workdays(0, 0)
    assert result_holiday is False, "Should return False when target is a holiday and start == end == 0"
