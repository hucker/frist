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


def test_work_day_yesterday_tomorrow_raise():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 3, 12, 0)
    b = Biz(target, ref, policy)
    try:
        _ = b.work_day.is_yesterday
        assert False, "Expected ValueError for work_day.is_yesterday"
    except ValueError:
        pass
    try:
        _ = b.work_day.is_tomorrow
        assert False, "Expected ValueError for work_day.is_tomorrow"
    except ValueError:
        pass


def test_biz_day_yesterday_tomorrow_raise():
    policy = BizPolicy(workdays=[0, 1, 2, 3, 4], holidays=set())
    target = dt.datetime(2025, 12, 3, 10, 0)  # Wed
    ref = dt.datetime(2025, 12, 3, 12, 0)
    b = Biz(target, ref, policy)
    try:
        _ = b.biz_day.is_yesterday
        assert False, "Expected ValueError for biz_day.is_yesterday"
    except ValueError:
        pass
    try:
        _ = b.biz_day.is_tomorrow
        assert False, "Expected ValueError for biz_day.is_tomorrow"
    except ValueError:
        pass
