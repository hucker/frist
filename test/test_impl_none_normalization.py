"""Verify public in_* methods normalize `end=None` to `start+1`.

These tests call the public, decorated `in_*` methods with a single-arg
form and compare to the explicit two-arg call where `end == start + 1` to
ensure the decorator normalization is applied consistently.
"""

import datetime as dt

from frist._cal import Cal
from frist._biz import Biz


def test_cal_public_none_normalization():
    ref = dt.datetime(2025, 3, 14, 12, 34, 56)
    cal = Cal(target_dt=ref, ref_dt=ref)

    # minutes
    assert cal.in_minutes(0) == cal.in_minutes(0, 1)
    # hours
    assert cal.in_hours(0) == cal.in_hours(0, 1)
    # days
    assert cal.in_days(0) == cal.in_days(0, 1)
    # weeks
    assert cal.in_weeks(0) == cal.in_weeks(0, 1)
    # months
    assert cal.in_months(0) == cal.in_months(0, 1)
    # quarters
    assert cal.in_quarters(0) == cal.in_quarters(0, 1)
    # years
    assert cal.in_years(0) == cal.in_years(0, 1)


def test_biz_public_none_normalization():
    # use a weekday ref so business checks true
    ref = dt.datetime(2025, 3, 14, 12, 34, 56)
    biz = Biz(target_time=ref, ref_time=ref)

    assert biz.in_business_days(0) == biz.in_business_days(0, 1)
    assert biz.in_working_days(0) == biz.in_working_days(0, 1)
    assert biz.in_fiscal_quarters(0) == biz.in_fiscal_quarters(0, 1)
    assert biz.in_fiscal_years(0) == biz.in_fiscal_years(0, 1)
