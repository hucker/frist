import datetime as dt
import pytest

from frist._biz import Biz
from frist._biz_policy import BizPolicy


def test_workday_fraction_zero_length_business_day():
    # set business hours to the same time -> zero-length business day
    policy = BizPolicy(start_of_business=dt.time(9, 0), end_of_business=dt.time(9, 0))
    ref = dt.datetime(2025, 1, 2, 12, 0)
    target = dt.datetime(2025, 1, 2, 9, 0)
    biz = Biz(target_dt=target, ref_dt=ref, policy=policy)
    assert biz._workday_fraction_at(target) == 0.0


def test_workday_fraction_before_and_after():
    policy = BizPolicy(start_of_business=dt.time(9, 0), end_of_business=dt.time(17, 0))
    # before start
    biz_before = Biz(target_dt=dt.datetime(2025, 1, 2, 8, 0), ref_dt=dt.datetime(2025, 1, 2, 12, 0), policy=policy)
    assert biz_before._workday_fraction_at(biz_before.target_dt) == 0.0
    # after end
    biz_after = Biz(target_dt=dt.datetime(2025, 1, 2, 18, 0), ref_dt=dt.datetime(2025, 1, 2, 12, 0), policy=policy)
    assert biz_after._workday_fraction_at(biz_after.target_dt) == 1.0


def test_age_days_helper_raises_when_target_after_ref():
    # target after ref should cause _age_days_helper to raise via public property
    ref = dt.datetime(2025, 1, 1, 0, 0)
    target = dt.datetime(2025, 1, 2, 0, 0)  # target > ref
    biz = Biz(target_dt=target, ref_dt=ref)
    with pytest.raises(ValueError):
        _ = biz.business_days


def test_move_n_days_zero_returns_same_date():
    policy = BizPolicy()
    biz = Biz(target_dt=dt.datetime(2025, 1, 1), ref_dt=dt.datetime(2025, 1, 1), policy=policy)
    d = dt.date(2025, 1, 10)
    assert biz._move_n_days(d, 0, count_business=True) == d
    assert biz._move_n_days(d, 0, count_business=False) == d


def test_get_fiscal_year_and_quarter_before_and_after_fy_start():
    # choose fiscal start in April (4)
    policy = BizPolicy(fiscal_year_start_month=4)
    # March 2025 should be fiscal year 2024 and quarter 4 (if fy starts Apr)
    dt_obj = dt.datetime(2025, 3, 15)
    assert Biz.get_fiscal_year(dt_obj, 4) == 2024
    assert Biz.get_fiscal_quarter(dt_obj, 4) == 4
    # April 2025 should be fy 2025, quarter 1
    dt_obj2 = dt.datetime(2025, 4, 2)
    assert Biz.get_fiscal_year(dt_obj2, 4) == 2025
    assert Biz.get_fiscal_quarter(dt_obj2, 4) == 1
