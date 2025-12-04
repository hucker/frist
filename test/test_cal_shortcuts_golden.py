"""
Golden (expected) results for Cal shortcut behaviors.
"""
import datetime as dt

import pytest

from frist import Biz, BizPolicy, Cal

# Use a reference datetime that yields stable week/month/quarter/year boundaries:
REF = dt.datetime(2025, 1, 13, 12, 0)  # Monday, Jan 13 2025 (week starts Monday)


@pytest.mark.parametrize(
    "shortcut, target_dt, expected",
    [
        # day shortcuts
        ("is_today", dt.datetime(2025, 1, 13, 0, 0), True),
        ("is_today", dt.datetime(2025, 1, 11, 12, 0), False),
        ("is_yesterday", dt.datetime(2025, 1, 12, 9, 0), True),
        ("is_tomorrow", dt.datetime(2025, 1, 14, 9, 0), True),
        # week shortcuts (ref week = 2025-01-13..2025-01-19)
        ("is_last_week", dt.datetime(2025, 1, 6, 0, 0), True),   # previous week
        ("is_this_week", dt.datetime(2025, 1, 15, 0, 0), True),   # same week
        ("is_next_week", dt.datetime(2025, 1, 20, 0, 0), True),   # next week
        # month shortcuts (ref month = Jan 2025)
        ("is_last_month", dt.datetime(2024, 12, 15, 0, 0), True),
        ("is_this_month", dt.datetime(2025, 1, 5, 0, 0), True),
        ("is_next_month", dt.datetime(2025, 2, 10, 0, 0), True),
        # quarter shortcuts (Q1=Jan-Mar for calendar quarters)
        ("is_last_quarter", dt.datetime(2024, 11, 15, 0, 0), True),  # Q4 2024
        ("is_this_quarter", dt.datetime(2025, 2, 1, 0, 0), True),    # Q1 2025
        ("is_next_quarter", dt.datetime(2025, 4, 1, 0, 0), True),    # Q2 2025
        # year shortcuts
        ("is_last_year", dt.datetime(2024, 6, 1, 0, 0), True),
        ("is_this_year", dt.datetime(2025, 7, 1, 0, 0), True),
        ("is_next_year", dt.datetime(2026, 3, 1, 0, 0), True),
        # obvious negatives for some units (sanity)
        ("is_last_month", dt.datetime(2025, 1, 2, 0, 0), False),
        ("is_this_week", dt.datetime(2025, 1, 6, 0, 0), False),
    ],
)
def test_cal_shortcuts_golden(shortcut: str, target_dt: dt.datetime, expected: bool) -> None:
    """
    Test Cal shortcuts with explicit golden datetimes (no parity comparisons).
    """
    c = Cal(target_dt=target_dt, ref_dt=REF)
    assert getattr(c, shortcut) is expected


@pytest.mark.parametrize(
    "shortcut, target_dt, expected",
    [
        # business-day / workday shortcuts
        ("is_business_this_day", dt.datetime(2025, 1, 13, 10, 0), True),
        ("is_business_last_day", dt.datetime(2025, 1, 10, 10, 0), True),
        ("is_business_next_day", dt.datetime(2025, 1, 14, 10, 0), True),
        ("is_workday_this_day", dt.datetime(2025, 1, 13, 10, 0), True),
        ("is_workday_last_day", dt.datetime(2025, 1, 10, 10, 0), True),
        ("is_workday_next_day", dt.datetime(2025, 1, 14, 10, 0), True),
        # fiscal shortcuts (calendar fiscal year starting Jan)
        ("is_this_fiscal_quarter", dt.datetime(2025, 2, 1, 0, 0), True),
        ("is_last_fiscal_quarter", dt.datetime(2024, 11, 15, 0, 0), True),
        ("is_next_fiscal_quarter", dt.datetime(2025, 4, 1, 0, 0), True),
        ("is_this_fiscal_year", dt.datetime(2025, 5, 1, 0, 0), True),
        ("is_last_fiscal_year", dt.datetime(2024, 6, 1, 0, 0), True),
        ("is_next_fiscal_year", dt.datetime(2026, 3, 1, 0, 0), True),
    ],
)
def test_biz_shortcuts_golden(shortcut: str, target_dt: dt.datetime, expected: bool) -> None:
    """
    Test Biz shortcuts with explicit golden datetimes. Uses default BizPolicy.
    """
    policy = BizPolicy()  # default policy; golden dates chosen to be unambiguous
    b = Biz(target_dt=target_dt, ref_dt=REF, policy=policy)
    assert getattr(b, shortcut) is expected


def test_unitnamespace_call_and_thru() -> None:
    """Exercise UnitNamespace call/between/thru/alias behaviors with golden expectations.

    This avoids parity checks while still exercising the UnitNamespace implementation
    paths (call, between alias, and thru property).
    """
    cal = Cal(target_dt=REF, ref_dt=REF)
    day_ns = cal.day

    # in_(0) should be True for ref==target
    assert day_ns.in_(0) is True
    # __call__ maps to in_
    assert day_ns(0) is True
    # between is an alias
    assert day_ns.between(0) is True
    # thru single-arg (inclusive) should also be True
    assert day_ns.thru(0) is True
    # thru two-arg for previous..current should be True (inclusive)
    assert day_ns.thru(-1, 0) is True

    # Also exercise a Biz UnitNamespace (work_day)
    policy = BizPolicy()
    b = Biz(target_dt=REF, ref_dt=REF, policy=policy)
    w_ns = b.work_day
    assert w_ns.in_(0) is True
    assert w_ns(0) is True
    assert w_ns.between(0) is True
    assert w_ns.thru(0) is True





@pytest.mark.parametrize("inclusive, expected", [
    # For offset -2, -1, 0, 1, 2 with window (-1, 1)
    # "both": [-1, 0, 1] are inside
    ("both", [False, True, True, True, False]),
    # "left": [-1, 0] are inside
    ("left", [False, True, True, False, False]),
    # "right": [0, 1] are inside
    ("right", [False, False, True, True, False]),
    # "neither": [0] is inside
    ("neither", [False, False, True, False, False]),
])
def test_between_edges_and_inside(inclusive: str, expected: list[bool]) -> None:
    """
    Test Cal.day.between for all inclusivity options, with offsets:
    outside_low (-2), edge (-1), inside (0), edge (1), outside_high (2)
    Window is (-1, 1)
    """
    ref_dt = dt.datetime(2025, 1, 13, 12, 0)
    results: list[bool] = []
    for offset in [-2, -1, 0, 1, 2]:
        target = ref_dt + dt.timedelta(days=offset)
        c = Cal(target_dt=target, ref_dt=ref_dt)
        results.append(c.day.between(-1, 1, inclusive=inclusive))
    assert results == expected