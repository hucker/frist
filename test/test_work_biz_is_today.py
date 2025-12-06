import datetime as dt

from frist import Biz, BizPolicy, Cal


def test_work_day_is_today_true_on_weekday():
    # Wednesday workday, target and ref same weekday
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 3, 12, 0)
    b = Biz(target, ref, policy)
    assert b.work_day.is_today is True


def test_work_day_is_today_false_on_weekend():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    target = dt.datetime(2025, 12, 6, 10, 0)  # Sat
    ref = dt.datetime(2025, 12, 6, 12, 0)
    b = Biz(target, ref, policy)
    assert b.work_day.is_today is False


def test_biz_day_is_today_false_on_holiday():
    # Holiday on Wed; business day should be false even if weekday
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays={"2025-12-03"})
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 3, 12, 0)
    b = Biz(target, ref, policy)
    assert b.biz_day.is_today is False


def test_biz_day_is_today_true_non_holiday_weekday():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    target = dt.datetime(2025, 12, 4, 10, 0)  # Thu
    ref = dt.datetime(2025, 12, 4, 12, 0)
    b = Biz(target, ref, policy)
    assert b.biz_day.is_today is True


def test_working_days_signed_direction():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    # Target earlier than ref yields positive working_days
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 4, 12, 0)    # Thu
    b_forward = Biz(target, ref, policy)
    pos_days = b_forward.work_day.working_days()
    assert pos_days > 0

    # Reversed order yields same magnitude but negative
    b_reverse = Biz(ref, target, policy)
    neg_days = b_reverse.work_day.working_days()
    assert neg_days == -pos_days


def test_business_days_signed_direction():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays={"2025-12-04"})
    # Wed to Fri with Thu a holiday: business_days counts Wed and Fri only
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 5, 12, 0)    # Fri
    b_forward = Biz(target, ref, policy)
    pos_days = b_forward.biz_day.business_days()
    assert pos_days > 0

    b_reverse = Biz(ref, target, policy)
    neg_days = b_reverse.biz_day.business_days()
    assert neg_days == -pos_days


def test_biz_day_yesterday_tomorrow_raise():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 3, 12, 0)
    b = Biz(target, ref, policy)
    import pytest
    with pytest.raises(ValueError):
        _ = b.biz_day.is_yesterday
    with pytest.raises(ValueError):
        _ = b.biz_day.is_tomorrow


def test_work_day_yesterday_tomorrow_raise():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 3, 12, 0)
    b = Biz(target, ref, policy)
    import pytest
    with pytest.raises(ValueError):
        _ = b.work_day.is_yesterday
    with pytest.raises(ValueError):
        _ = b.work_day.is_tomorrow
