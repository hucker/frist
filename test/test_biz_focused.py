import datetime as dt

from frist._biz import Biz
from frist._cal_policy import CalendarPolicy


def test_multi_day_fraction_working_and_business_days():
    # Jan 1 2024 12:00 (Mon) to Jan 4 2024 15:00 (Thu) — spans 4 calendar days
    start = dt.datetime(2024, 1, 1, 12, 0)
    end = dt.datetime(2024, 1, 4, 15, 0)
    policy = CalendarPolicy()  # default 9-17, Mon-Fri
    biz = Biz(start, end, policy)

    # Expected fractions:
    # Jan 1: 12:00-17:00 = 5/8 = 0.625
    # Jan 2: full workday = 1.0
    # Jan 3: full workday = 1.0
    # Jan 4: 09:00-15:00 = 6/8 = 0.75
    expected = 0.625 + 1.0 + 1.0 + 0.75

    assert abs(biz.working_days() - expected) < 1e-9
    assert abs(biz.business_days() - expected) < 1e-9


def test_multi_day_with_middle_holiday():
    # Same span but mark Jan 3 as a holiday — business_days should exclude it
    start = dt.datetime(2024, 1, 1, 12, 0)
    end = dt.datetime(2024, 1, 4, 15, 0)
    holidays = {"2024-01-03"}
    policy = CalendarPolicy(holidays=holidays)
    biz = Biz(start, end, policy)

    expected_working = 0.625 + 1.0 + 1.0 + 0.75
    expected_business = expected_working - 1.0  # Jan 3 becomes 0.0

    assert abs(biz.working_days() - expected_working) < 1e-9
    assert abs(biz.business_days() - expected_business) < 1e-9


def test_in_working_and_business_days_range_with_holiday():
    # Reference is Jan 4 2024. Target Jan 2 should be in working_days(-2,0)
    ref = dt.datetime(2024, 1, 4, 12, 0)
    target = dt.datetime(2024, 1, 2, 10, 0)
    policy = CalendarPolicy()
    biz = Biz(target, ref, policy)

    assert biz.in_working_days(-2, 0) is True
    assert biz.in_business_days(-2, 0) is True

    # If Jan 2 is a holiday, in_business_days should be False but in_working_days still True
    policy2 = CalendarPolicy(holidays={"2024-01-02"})
    biz2 = Biz(target, ref, policy2)
    assert biz2.in_working_days(-2, 0) is True
    assert biz2.in_business_days(-2, 0) is False
