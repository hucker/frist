"""Targeted tests to cover small alternate branches in `src/frist/_cal.py`.

These include:
- invalid inputs to `normalize_weekday` that raise ValueError
- constructing `Cal` with numeric timestamps and invalid types raising TypeError
- verifying `is_*` shortcut properties delegate to `in_*` methods
"""
import datetime as dt
import pytest

from frist._cal import normalize_weekday, Cal


def test_normalize_weekday_invalid_raises() -> None:
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("not-a-day")


def test_cal_init_numeric_and_typeerror() -> None:
    ref = dt.datetime(2025, 3, 15, 12, 0, 0)
    # numeric timestamp (int)
    ts = int(ref.timestamp())
    c = Cal(target_dt=ts, ref_dt=ts)
    assert isinstance(c.target_dt, dt.datetime)
    assert isinstance(c.ref_dt, dt.datetime)

    # invalid target_dt type
    with pytest.raises(TypeError, match="target_dt must be datetime, float, or int"):
        Cal(target_dt="bad", ref_dt=ref)

    # invalid ref_dt type
    with pytest.raises(TypeError, match="ref_dt must be datetime, float, or int"):
        Cal(target_dt=ref, ref_dt="bad")


def test_cal_shortcut_properties_delegate_to_methods() -> None:
    ref = dt.datetime(2025, 4, 10, 12, 0, 0)
    # choose a target equal to ref for 'this' shortcuts
    c = Cal(target_dt=ref, ref_dt=ref)

    # Golden assertions for shortcuts (explicit expectations, not parity checks)
    assert c.is_today is True
    assert c.is_this_week is True
    assert c.is_this_month is True
    assert c.is_this_quarter is True
    assert c.is_this_year is True

    # last/next variants
    assert c.is_last_week is False
    assert c.is_next_week is False
    assert c.is_last_month is False
    assert c.is_next_month is False
    assert c.is_last_quarter is False
    assert c.is_next_quarter is False
    assert c.is_last_year is False
    assert c.is_next_year is False

    # explicit yesterday/tomorrow checks using golden expectations
    ref2 = dt.datetime(2025, 4, 11, 12, 0, 0)
    cal_y = Cal(target_dt=ref2 - dt.timedelta(days=1), ref_dt=ref2)
    cal_t = Cal(target_dt=ref2 + dt.timedelta(days=1), ref_dt=ref2)

    assert cal_y.is_yesterday is True
    assert cal_t.is_tomorrow is True


def test_normalize_weekday_pandas_prefix_invalid() -> None:
    # ensure pandas-style prefix branch is exercised and raises for unknown code
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("w-xyz")
