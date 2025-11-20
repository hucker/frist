import datetime as dt
import pytest

from frist._biz import Biz
from frist._cal_policy import CalendarPolicy


def test_biz_basic_business_fraction():
    """Biz uses CalendarPolicy to compute business fractions on a normal business day."""
    policy: CalendarPolicy = CalendarPolicy(holidays=set())

    # Wednesday Nov 19 2025, 10:00 -> 17:00 (7 business hours of 8)
    target: dt.datetime = dt.datetime(2025, 11, 19, 10, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 19, 17, 0)

    biz: Biz = Biz(target, ref, policy)

    assert biz.is_workday is True
    assert biz.is_business_day is True

    # business_days() between 10:00 and 17:00 should be 7/8 = 0.875
    assert pytest.approx(biz.business_days(), rel=1e-6) == 0.875
    # working_days should match business_days when no holiday present
    assert pytest.approx(biz.working_days(), rel=1e-6) == pytest.approx(biz.business_days(), rel=1e-6)


def test_biz_holiday_affects_business_but_not_working():
    """When the date is a policy holiday, business_days become 0 but working_days still count weekdays."""
    holiday_date: str = "2025-11-19"
    policy: CalendarPolicy = CalendarPolicy(holidays={holiday_date})

    target: dt.datetime = dt.datetime(2025, 11, 19, 9, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 19, 17, 0)

    biz: Biz = Biz(target, ref, policy)

    assert biz.holiday is True
    assert biz.is_workday is True  # weekday remains a workday
    assert biz.is_business_day is False  # but it's a holiday

    # business_days should be zero for a holiday spanning the full business day
    assert pytest.approx(biz.business_days(), rel=1e-6) == 0.0

    # working_days ignores holidays and counts the business-hours fraction
    assert pytest.approx(biz.working_days(), rel=1e-6) == 1.0


def test_in_business_and_working_days_ranges():
    """Verify range-membership helpers using CalendarPolicy (business vs working behavior)."""
    policy: CalendarPolicy = CalendarPolicy(holidays=set())

    # ref is 2025-11-20 (Thursday). target is previous day (Wednesday)
    target: dt.datetime = dt.datetime(2025, 11, 19, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 20, 12, 0)

    biz: Biz = Biz(target, ref, policy)

    # Using a window of [-1, 0] business-days from ref should include the 19th
    assert biz.in_business_days(-1, 0) is True

    # Working-days window should also include the 19th
    assert biz.in_working_days(-1, 0) is True


def test_in_fiscal_quarters_and_years():
    """Verify Biz.in_fiscal_quarters and Biz.in_fiscal_years behavior for fiscal year starting in April."""
    policy: CalendarPolicy = CalendarPolicy(fiscal_year_start_month=4)

    # Reference in FY2025 (July 15, 2025 -> FY2025, Q2)
    ref: dt.datetime = dt.datetime(2025, 7, 15, 12, 0)

    # Target in same fiscal quarter (Q2): July 1, 2025
    target_q2: dt.datetime = dt.datetime(2025, 7, 1, 9, 0)
    biz_q2: Biz = Biz(target_q2, ref, policy)
    assert biz_q2.in_fiscal_quarters(0) is True

    # Target in previous quarter (Q1): May 15, 2025
    target_q1: dt.datetime = dt.datetime(2025, 5, 15, 9, 0)
    biz_q1: Biz = Biz(target_q1, ref, policy)
    assert biz_q1.in_fiscal_quarters(-1, 0) is True

    # Fiscal year checks: target in same fiscal year (Nov 2025)
    target_same_fy: dt.datetime = dt.datetime(2025, 11, 1, 12, 0)
    biz_same_fy: Biz = Biz(target_same_fy, ref, policy)
    assert biz_same_fy.in_fiscal_years(0) is True

    # Target in next fiscal year: April 1, 2026 (start of FY2026)
    target_next_fy: dt.datetime = dt.datetime(2026, 4, 1, 9, 0)
    biz_next_fy: Biz = Biz(target_next_fy, ref, policy)
    assert biz_next_fy.in_fiscal_years(1) is True


def test_in_business_working_days_start_greater_than_end_raises():
    """in_business_days and in_working_days should raise when start > end."""
    policy: CalendarPolicy = CalendarPolicy(holidays=set())
    target: dt.datetime = dt.datetime(2025, 11, 19, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 20, 12, 0)

    biz: Biz = Biz(target, ref, policy)

    with pytest.raises(ValueError):
        biz.in_business_days(1, 0)

    with pytest.raises(ValueError):
        biz.in_working_days(1, 0)


def test_biz_repr_contains_fields():
    """`repr(Biz)` should include target_time, ref_time, and policy information."""
    policy: CalendarPolicy = CalendarPolicy(holidays=set())
    target: dt.datetime = dt.datetime(2025, 11, 19, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 20, 12, 0)

    biz: Biz = Biz(target, ref, policy)
    r: str = repr(biz)

    assert r.startswith("<Biz ")
    # repr of the datetimes should appear
    assert repr(target) in r
    assert repr(ref) in r
    # policy type name should appear
    assert "CalendarPolicy" in r


def test_in_working_days_returns_false_for_non_workday():
    """If the target day is not a workday (weekend) `in_working_days` returns False."""
    policy: CalendarPolicy = CalendarPolicy(holidays=set())

    # Sunday Nov 23, 2025 is a weekend (not a workday)
    target: dt.datetime = dt.datetime(2025, 11, 23, 12, 0)
    # Reference on the following Monday
    ref: dt.datetime = dt.datetime(2025, 11, 24, 12, 0)

    biz: Biz = Biz(target, ref, policy)

    assert biz.is_workday is False
    # Even if asking for a range including the target day, it should be False
    assert biz.in_working_days(0, 0) is False
    assert biz.in_working_days(-1, 0) is False


def test_fiscal_methods_raise_on_start_greater_than_end():
    """in_fiscal_quarters and in_fiscal_years should raise when start > end (verify_start_end)."""
    policy: CalendarPolicy = CalendarPolicy(fiscal_year_start_month=4)
    # ref is mid-July 2025
    ref: dt.datetime = dt.datetime(2025, 7, 15, 12, 0)
    # target earlier in same fiscal year
    target: dt.datetime = dt.datetime(2025, 5, 1, 9, 0)

    biz: Biz = Biz(target, ref, policy)

    with pytest.raises(ValueError):
        biz.in_fiscal_quarters(1, 0)

    with pytest.raises(ValueError):
        biz.in_fiscal_years(2, 1)


def test_multi_day_fraction_working_and_business_days():
    # Jan 1 2024 12:00 (Mon) to Jan 4 2024 15:00 (Thu)  spans 4 calendar days
    start: dt.datetime = dt.datetime(2024, 1, 1, 12, 0)
    end: dt.datetime = dt.datetime(2024, 1, 4, 15, 0)
    policy: CalendarPolicy = CalendarPolicy()  # default 9-17, Mon-Fri
    biz: Biz = Biz(start, end, policy)

    # Expected fractions:
    # Jan 1: 12:00-17:00 = 5/8 = 0.625
    # Jan 2: full workday = 1.0
    # Jan 3: full workday = 1.0
    # Jan 4: 09:00-15:00 = 6/8 = 0.75
    expected: float = 0.625 + 1.0 + 1.0 + 0.75

    assert abs(biz.working_days() - expected) < 1e-9
    assert abs(biz.business_days() - expected) < 1e-9


def test_multi_day_with_middle_holiday():
    # Same span but mark Jan 3 as a holiday  business_days should exclude it
    start: dt.datetime = dt.datetime(2024, 1, 1, 12, 0)
    end: dt.datetime = dt.datetime(2024, 1, 4, 15, 0)
    holidays: Set[str] = {"2024-01-03"}
    policy: CalendarPolicy = CalendarPolicy(holidays=holidays)
    biz: Biz = Biz(start, end, policy)

    expected_working: float = 0.625 + 1.0 + 1.0 + 0.75
    expected_business: float = expected_working - 1.0  # Jan 3 becomes 0.0

    assert abs(biz.working_days() - expected_working) < 1e-9
    assert abs(biz.business_days() - expected_business) < 1e-9


def test_in_working_and_business_days_range_with_holiday():
    # Reference is Jan 4 2024. Target Jan 2 should be in working_days(-2,0)
    ref: dt.datetime = dt.datetime(2024, 1, 4, 12, 0)
    target: dt.datetime = dt.datetime(2024, 1, 2, 10, 0)
    policy: CalendarPolicy = CalendarPolicy()
    biz: Biz = Biz(target, ref, policy)

    assert biz.in_working_days(-2, 0) is True
    assert biz.in_business_days(-2, 0) is True

    # If Jan 2 is a holiday, in_business_days should be False but in_working_days still True
    policy2: CalendarPolicy = CalendarPolicy(holidays={"2024-01-02"})
    biz2: Biz = Biz(target, ref, policy2)
    assert biz2.in_working_days(-2, 0) is True
    assert biz2.in_business_days(-2, 0) is False


def test_business_days_raises_when_target_after_ref():
    """business_days() should raise ValueError when target_time > ref_time"""
    target: dt.datetime = dt.datetime(2025, 1, 5, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 1, 4, 12, 0)
    policy: CalendarPolicy = CalendarPolicy()
    biz: Biz = Biz(target, ref, policy)

    with pytest.raises(ValueError) as exc:
        biz.business_days()
    assert "target_time must not be after ref_time" in str(exc.value), "business_days should raise on target>ref"


def test_working_days_raises_when_target_after_ref():
    """working_days() should raise ValueError when target_time > ref_time"""
    target: dt.datetime = dt.datetime(2025, 1, 5, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 1, 4, 12, 0)
    policy: CalendarPolicy = CalendarPolicy()
    biz: Biz = Biz(target, ref, policy)

    with pytest.raises(ValueError) as exc:
        biz.working_days()
    assert "target_time must not be after ref_time" in str(exc.value), "working_days should raise on target>ref"