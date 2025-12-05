import datetime as dt

from frist import Cal


def test_day_unit_shortcuts_today_yesterday_tomorrow():
    ref = dt.datetime(2025, 12, 5, 12, 0)
    # today
    assert Cal(dt.datetime(2025, 12, 5, 9, 0), ref).day.is_today is True
    # yesterday
    assert Cal(dt.datetime(2025, 12, 4, 9, 0), ref).day.is_yesterday is True
    # tomorrow
    assert Cal(dt.datetime(2025, 12, 6, 9, 0), ref).day.is_tomorrow is True


def test_day_unit_in_impl_half_open_boundaries():
    ref = dt.datetime(2025, 12, 5, 0, 0)
    cal = Cal(dt.datetime(2025, 12, 5, 23, 59, 59), ref)
    # window [-1, 1) covers yesterday and today (exclusive end at tomorrow)
    assert cal.day.in_(-1, 1) is True
    # end exclusive: a time exactly at start of tomorrow is not included
    cal2 = Cal(dt.datetime(2025, 12, 6, 0, 0), ref)
    assert cal2.day.in_(-1, 1) is False
