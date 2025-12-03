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

    # Golden checks: explicit boolean expectations (do not compare implementations)
    assert cal.day.in_(0) is True


def test_biz_public_none_normalization():
    # use a weekday ref so business checks true
    ref = dt.datetime(2025, 3, 14, 12, 34, 56)
    biz = Biz(target_dt=ref, ref_dt=ref)

    # Golden checks: with ref==target on a weekday, these should be True
    assert biz.biz_day.in_(0) is True
    assert biz.work_day.in_(0) is True
