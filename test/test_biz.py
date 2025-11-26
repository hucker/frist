"""Comprehensive tests for `Biz` behavior.

This module exercises `Biz` calculations including `working_days`,
`business_days`, range membership helpers, and fiscal helpers. Tests
use explicit dates and follow the Arrange/Act/Assert (AAA) pattern.
"""

import datetime as dt
import pytest
from typing import Set

from frist import Biz, BizPolicy


def test_biz_basic_business_fraction():
    """Biz uses BizPolicy to compute business fractions on a normal business day.

    Arrange: create a Biz spanning 10:00 -> 17:00 on a Wednesday.
    Act: compute `business_days` and `working_days`.
    Assert: fractions match expected values.
    """
    policy: BizPolicy = BizPolicy(holidays=set())

    # Arrange
    target: dt.datetime = dt.datetime(2025, 11, 19, 10, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 19, 17, 0)

    # Act
    biz: Biz = Biz(target, ref, policy)

    # Assert
    assert biz.is_workday is True, "target should be a workday"
    assert biz.is_business_day is True, "target should be a business day"

    # business_days() between 10:00 and 17:00 should be 7/8 = 0.875
    assert biz.business_days == pytest.approx(0.875, rel=1e-6), "business_days fraction mismatch"
    # working_days should match business_days when no holiday present
    assert biz.working_days == pytest.approx(biz.business_days, rel=1e-6), "working_days should equal business_days when no holidays"


def test_biz_holiday_affects_business_but_not_working():
    """When the date is a policy holiday, business_days become 0 but working_days still count weekdays."""
    holiday_date: str = "2025-11-19"
    policy: BizPolicy = BizPolicy(holidays={holiday_date})

    # Arrange
    target: dt.datetime = dt.datetime(2025, 11, 19, 9, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 19, 17, 0)

    # Act
    biz: Biz = Biz(target, ref, policy)

    # Assert
    assert biz.holiday is True, "Holiday property should be True for the target date"
    assert biz.is_workday is True, "Weekday should still be considered a workday"
    assert biz.is_business_day is False, "Holiday should not be a business day"

    # business_days should be zero for a holiday spanning the full business day
    assert biz.business_days == pytest.approx(0.0, rel=1e-6), "business_days should be 0.0 for a full-day holiday"

    # working_days ignores holidays and counts the business-hours fraction
    assert biz.working_days == pytest.approx(1.0, rel=1e-6), "working_days should reflect weekday fraction regardless of holiday"


def test_in_business_and_working_days_ranges():
    """Verify range-membership helpers using BizPolicy (business vs working behavior)."""
    policy: BizPolicy = BizPolicy(holidays=set())

    # Arrange - ref is 2025-11-20 (Thursday). target is previous day (Wednesday)
    target: dt.datetime = dt.datetime(2025, 11, 19, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 20, 12, 0)

    # Act
    biz: Biz = Biz(target, ref, policy)

    # Assert - Using a window of [-1, 0] business-days from ref should include the 19th
    assert biz.in_business_days(-1, 0) is True, "19th should be within business-days(-1,0)"

    # Assert - Working-days window should also include the 19th
    assert biz.in_working_days(-1, 0) is True, "19th should be within working-days(-1,0)"


def test_in_fiscal_quarters_and_years():
    """Verify Biz.in_fiscal_quarters and Biz.in_fiscal_years behavior for fiscal year starting in April."""
    policy: BizPolicy = BizPolicy(fiscal_year_start_month=4)

    # Arrange - Reference in FY2025 (July 15, 2025 -> FY2025, Q2)
    ref: dt.datetime = dt.datetime(2025, 7, 15, 12, 0)

    # Act / Assert - Target in same fiscal quarter (Q2): July 1, 2025
    target_q2: dt.datetime = dt.datetime(2025, 7, 1, 9, 0)
    biz_q2: Biz = Biz(target_q2, ref, policy)
    assert biz_q2.in_fiscal_quarters(0) is True, "Target in same fiscal quarter should be True"

    # Act / Assert - Target in previous quarter (Q1): May 15, 2025
    target_q1: dt.datetime = dt.datetime(2025, 5, 15, 9, 0)
    biz_q1: Biz = Biz(target_q1, ref, policy)
    assert biz_q1.in_fiscal_quarters(-1, 0) is True, "Target in previous fiscal quarter should be True"

    # Act / Assert - Fiscal year checks: target in same fiscal year (Nov 2025)
    target_same_fy: dt.datetime = dt.datetime(2025, 11, 1, 12, 0)
    biz_same_fy: Biz = Biz(target_same_fy, ref, policy)
    assert biz_same_fy.in_fiscal_years(0) is True, "Target in same fiscal year should be True"

    # Act / Assert - Target in next fiscal year: April 1, 2026 (start of FY2026)
    target_next_fy: dt.datetime = dt.datetime(2026, 4, 1, 9, 0)
    biz_next_fy: Biz = Biz(target_next_fy, ref, policy)
    assert biz_next_fy.in_fiscal_years(1) is True, "Target in next fiscal year should be True"


def test_in_business_working_days_start_greater_than_end_raises():
    """in_business_days and in_working_days should raise when start > end."""
    policy: BizPolicy = BizPolicy(holidays=set())
    target: dt.datetime = dt.datetime(2025, 11, 19, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 20, 12, 0)

    biz: Biz = Biz(target, ref, policy)

    with pytest.raises(ValueError):
        biz.in_business_days(1, 0)

    with pytest.raises(ValueError):
        biz.in_working_days(1, 0)


def test_biz_repr_contains_fields():
    """`repr(Biz)` should include target_time, ref_time, and policy information."""
    policy: BizPolicy = BizPolicy(holidays=set())
    target: dt.datetime = dt.datetime(2025, 11, 19, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 11, 20, 12, 0)

    biz: Biz = Biz(target, ref, policy)
    r: str = repr(biz)

    assert r.startswith("<Biz ")
    # repr of the datetimes should appear
    assert repr(target) in r
    assert repr(ref) in r
    # policy type name should appear
    assert "BizPolicy" in r


def test_in_working_days_returns_false_for_non_workday():
    """If the target day is not a workday (weekend) `in_working_days` returns False."""
    policy: BizPolicy = BizPolicy(holidays=set())

    # Sunday Nov 23, 2025 is a weekend (not a workday)
    target: dt.datetime = dt.datetime(2025, 11, 23, 12, 0)
    # Reference on the following Monday
    ref: dt.datetime = dt.datetime(2025, 11, 24, 12, 0)

    biz: Biz = Biz(target, ref, policy)

    assert biz.is_workday is False
    # Even if asking for a range including the target day, it should be False
    assert biz.in_working_days(0, 1) is False
    assert biz.in_working_days(-1, 0) is False


def test_fiscal_methods_raise_on_start_greater_than_end():
    """in_fiscal_quarters and in_fiscal_years should raise when start > end (verify_start_end)."""
    policy: BizPolicy = BizPolicy(fiscal_year_start_month=4)
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
    policy: BizPolicy = BizPolicy()  # default 9-17, Mon-Fri
    biz: Biz = Biz(start, end, policy)

    # Expected fractions:
    # Jan 1: 12:00-17:00 = 5/8 = 0.625
    # Jan 2: full workday = 1.0
    # Jan 3: full workday = 1.0
    # Jan 4: 09:00-15:00 = 6/8 = 0.75
    expected: float = 0.625 + 1.0 + 1.0 + 0.75

    assert abs(biz.working_days - expected) < 1e-9
    assert abs(biz.business_days - expected) < 1e-9


def test_multi_day_with_middle_holiday():
    # Same span but mark Jan 3 as a holiday  business_days should exclude it
    start: dt.datetime = dt.datetime(2024, 1, 1, 12, 0)
    end: dt.datetime = dt.datetime(2024, 1, 4, 15, 0)
    holidays: Set[str] = {"2024-01-03"}
    policy: BizPolicy = BizPolicy(holidays=holidays)
    biz: Biz = Biz(start, end, policy)

    expected_working: float = 0.625 + 1.0 + 1.0 + 0.75
    expected_business: float = expected_working - 1.0  # Jan 3 becomes 0.0

    assert abs(biz.working_days - expected_working) < 1e-9
    assert abs(biz.business_days - expected_business) < 1e-9


def test_in_working_and_business_days_range_with_holiday():
    # Reference is Jan 4 2024. Target Jan 2 should be in working_days(-2,0)
    ref: dt.datetime = dt.datetime(2024, 1, 4, 12, 0)
    target: dt.datetime = dt.datetime(2024, 1, 2, 10, 0)
    policy: BizPolicy = BizPolicy()
    biz: Biz = Biz(target, ref, policy)

    assert biz.in_working_days(-2, 0) is True
    assert biz.in_business_days(-2, 0) is True

    # If Jan 2 is a holiday, in_business_days should be False but in_working_days still True
    policy2: BizPolicy = BizPolicy(holidays={"2024-01-02"})
    biz2: Biz = Biz(target, ref, policy2)
    assert biz2.in_working_days(-2, 0) is True
    assert biz2.in_business_days(-2, 0) is False


def test_business_days_raises_when_target_after_ref():
    """business_days() should raise ValueError when target_time > ref_time"""
    target: dt.datetime = dt.datetime(2025, 1, 5, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 1, 4, 12, 0)
    policy: BizPolicy = BizPolicy()
    biz: Biz = Biz(target, ref, policy)

    with pytest.raises(ValueError) as exc:
        _:float = biz.business_days
    assert "must not be after" in str(exc.value), "business_days should raise on target>ref"


def test_working_days_raises_when_target_after_ref():
    """working_days() should raise ValueError when target_time > ref_time"""
    target: dt.datetime = dt.datetime(2025, 1, 5, 12, 0)
    ref: dt.datetime = dt.datetime(2025, 1, 4, 12, 0)
    policy: BizPolicy = BizPolicy()
    biz: Biz = Biz(target, ref, policy)

    with pytest.raises(ValueError) as exc:
        _:float = biz.working_days
    assert "must not be after" in str(exc.value), "working_days should raise on target>ref"



def test_working_days_basic_weekday() -> None:
    """Biz.working_days returns 1.0 for a full weekday."""
    start = dt.datetime(2024, 1, 2, 0, 0, 0)  # Tuesday
    end = dt.datetime(2024, 1, 2, 23, 59, 59)
    biz = Biz(start, end)
    assert abs(biz.working_days - 1.0) < 1e-6, "Should be 1.0 for full weekday"


def test_working_days_weekend() -> None:
    """Biz.working_days returns 0.0 for a weekend day."""
    start = dt.datetime(2024, 1, 6, 0, 0, 0)  # Saturday
    end = dt.datetime(2024, 1, 6, 23, 59, 59)
    biz:Biz = Biz(target_time=start,ref_time= end)
    assert biz.working_days == 0.0, "Should be 0.0 for weekend"


def test_working_days_partial_day() -> None:
    """BizAge.working_days returns correct fraction for partial weekday."""
    start = dt.datetime(2024, 1, 2, 12, 0, 0)  # Tuesday noon
    end = dt.datetime(2024, 1, 2, 18, 0, 0)
    biz:Biz=Biz(start,end)
    # Business hours: 9:00 to 17:00 (8 hours)
    # Noon to 17:00 = 5 hours (within business hours)
    # 17:00 to 18:00 is outside business hours, so only noon to 17:00 counts
    expected = 5 / 8  # 5 hours out of 8 business hours
    assert abs(biz.working_days - expected) < 1e-6, "Should match fraction of business hours"


def test_working_days_multiple_days() -> None:
    """Biz.working_days sums multiple weekdays, skips weekends."""
    start = dt.datetime(2024, 1, 5, 12, 0, 0)  # Friday noon
    end = dt.datetime(2024, 1, 8, 12, 0, 0)    # Monday noon
    biz = Biz(start, end)
    # Friday: half day, Saturday/Sunday: 0, Monday: half day
    expected = 0.5 + 0.5
    assert abs(biz  .working_days - expected) < 1e-6, "Should sum only working day fractions"


def test_work_business_days_holiday() -> None:
    """Biz.working_days returns 0.0 for a holiday (using custom BizPolicy)."""
    # Jan 2, 2024 is a holiday
    cal = BizPolicy(holidays={"2024-01-02"})
    start = dt.datetime(2024, 1, 2, 0, 0, 0)
    end = dt.datetime(2024, 1, 2, 23, 59, 59)
    biz = Biz(start, end, policy=cal)
    assert biz.working_days == 1.0, "Should be 0.0 for workday"
    assert biz.business_days == 0.0, "Should be 0.0 for holiday"


def test_working_days_start_after_end() -> None:
    """Biz.working_days returns 0.0 if start_time > end_time."""
    start = dt.datetime(2024, 1, 3, 12, 0, 0)
    end = dt.datetime(2024, 1, 2, 12, 0, 0)
    biz:Biz = Biz(start, end)
    with pytest.raises(ValueError, match="must not be after"):
        _ = biz.working_days