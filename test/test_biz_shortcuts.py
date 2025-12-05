"""Five-case tests for `Biz` shortcut properties.

These tests verify the five canonical boundary positions for each shortcut:
below-lower, on-lower, interior (above-lower), on-upper (exclusive), above-upper.

Shortcuts covered:
- Day-level: is_business_day_yesterday / is_business_day_today / is_business_day_tomorrow
             is_workday_yesterday / is_workday_today / is_workday_tomorrow
- Fiscal: is_last_fiscal_quarter / is_this_fiscal_quarter / is_next_fiscal_quarter
          is_last_fiscal_year / is_this_fiscal_year / is_next_fiscal_year
"""
from __future__ import annotations

import datetime as dt

from frist import Biz, BizPolicy


def _check_five_biz(prop: str, ref: dt.datetime, policy: BizPolicy,
                    dt_below: dt.datetime, dt_on_lower: dt.datetime,
                    dt_above_lower: dt.datetime, dt_on_upper: dt.datetime,
                    dt_above_upper: dt.datetime) -> None:
    """Assert five-case expectations for Biz(...).{prop} given `ref` and `policy`.

    Uses `getattr(Biz(t, ref, policy), prop)` to evaluate the boolean.
    """
    # Arrange & Act
    def actual(t: dt.datetime) -> bool:
        return getattr(Biz(t, ref, policy), prop)

    # Assert
    expected = [False, True, True, False, False]
    actuals = [
        actual(dt_below),
        actual(dt_on_lower),
        actual(dt_above_lower),
        actual(dt_on_upper),
        actual(dt_above_upper)
    ]
    assert actuals[0] is expected[0], (
        f"{prop}: below-lower should be False ({dt_below})"
    )
    assert actuals[1] is expected[1], (
        f"{prop}: on-lower should be True ({dt_on_lower})"
    )
    assert actuals[2] is expected[2], (
        f"{prop}: above-lower (interior) should be True ({dt_above_lower})"
    )
    assert actuals[3] is expected[3], (
        f"{prop}: on-upper should be False (exclusive) ({dt_on_upper})"
    )
    assert actuals[4] is expected[4], (
        f"{prop}: above-upper should be False ({dt_above_upper})"
    )


def test_day_shortcuts_five_cases() -> None:
    """Day-level business/workday shortcuts five-case coverage."""
    """
    Day-level business/workday shortcuts five-case coverage.
    """
    # Arrange
    ref = dt.datetime(2025, 1, 15, 12, 0)  # Wednesday
    policy = BizPolicy()  # default Mon-Fri workdays, no holidays
    lower_date = ref.date()
    upper_date = ref.date() + dt.timedelta(days=1)
    dt_below = dt.datetime.combine(lower_date - dt.timedelta(days=1), dt.time(12, 0))
    dt_on_lower = dt.datetime.combine(lower_date, dt.time(12, 0))
    dt_above_lower = dt.datetime.combine(lower_date, dt.time(18, 0))
    dt_on_upper = dt.datetime.combine(upper_date, dt.time(12, 0))
    dt_above_upper = dt.datetime.combine(
        upper_date + dt.timedelta(days=1), dt.time(12, 0)
    )
    # Act & Assert
    # Act & Assert
    _check_five_biz(
        "is_business_day_today", ref, policy,
        dt_below, dt_on_lower, dt_above_lower, dt_on_upper, dt_above_upper
    )
    _check_five_biz(
        "is_workday_today", ref, policy,
        dt_below, dt_on_lower, dt_above_lower, dt_on_upper, dt_above_upper
    )


def test_business_vs_workday_holiday_shortcuts() -> None:
    """Show difference between business and workday shortcuts when a holiday is present.

    With a policy holiday on 2025-07-04 (Friday), the 'last' business-day before
    reference 2025-07-07 will be Thursday 2025-07-03 (the holiday is skipped),
    but the workday shortcut will still consider the holiday a workday.
    """
    """
    Show difference between business and workday shortcuts when a holiday is present.
    """
    # Arrange
    ref = dt.datetime(2025, 7, 7, 12, 0)  # Monday
    policy = BizPolicy(holidays={"2025-07-04"})
    dt_thu = dt.datetime(2025, 7, 3, 12, 0)
    dt_fri_hol = dt.datetime(2025, 7, 4, 12, 0)
    # Act & Assert
    expected_business_last_day_thu = True
    expected_business_last_day_fri = False
    expected_workday_last_day_fri = True
    actual_business_last_day_thu = Biz(dt_thu, ref, policy).is_business_day_yesterday
    actual_business_last_day_fri = Biz(dt_fri_hol, ref, policy).is_business_day_yesterday
    actual_workday_last_day_fri = Biz(dt_fri_hol, ref, policy).is_workday_yesterday
    assert actual_business_last_day_thu is expected_business_last_day_thu
    assert actual_business_last_day_fri is expected_business_last_day_fri
    assert actual_workday_last_day_fri is expected_workday_last_day_fri


def test_fiscal_quarter_shortcuts_five_cases() -> None:
    """Fiscal-quarter shortcuts five-case coverage (fiscal year start = April)."""
    """
    Fiscal-quarter shortcuts five-case coverage (fiscal year start = April).
    """
    # Arrange
    policy = BizPolicy(fiscal_year_start_month=4)
    ref = dt.datetime(2025, 7, 15, 12, 0)
    # Act & Assert
    _check_five_biz(
        "is_last_fiscal_quarter",
        ref,
        policy,
        dt.datetime(2025, 1, 15, 12, 0),
        dt.datetime(2025, 4, 1, 12, 0),
        dt.datetime(2025, 5, 15, 12, 0),
        dt.datetime(2025, 7, 1, 0, 0),
        dt.datetime(2025, 8, 1, 12, 0),
    )
    _check_five_biz(
        "is_this_fiscal_quarter",
        ref,
        policy,
        dt.datetime(2025, 6, 30, 23, 59),
        dt.datetime(2025, 7, 1, 12, 0),
        dt.datetime(2025, 8, 15, 12, 0),
        dt.datetime(2025, 10, 1, 0, 0),
        dt.datetime(2025, 12, 1, 12, 0),
    )


def test_fiscal_year_shortcuts_five_cases() -> None:
    """Fiscal-year shortcuts five-case coverage (fiscal year start = April)."""
    """
    Fiscal-year shortcuts five-case coverage (fiscal year start = April).
    """
    # Arrange
    policy = BizPolicy(fiscal_year_start_month=4)
    ref = dt.datetime(2025, 7, 15, 12, 0)
    # Act & Assert
    _check_five_biz(
        "is_last_fiscal_year",
        ref,
        policy,
        dt.datetime(2023, 12, 31, 12, 0),
        dt.datetime(2024, 4, 1, 12, 0),
        dt.datetime(2024, 10, 1, 12, 0),
        dt.datetime(2025, 4, 1, 0, 0),
        dt.datetime(2026, 6, 1, 12, 0),
    )
    _check_five_biz(
        "is_this_fiscal_year",
        ref,
        policy,
        dt.datetime(2025, 3, 31, 23, 59),
        dt.datetime(2025, 4, 1, 0, 0),
        dt.datetime(2025, 10, 1, 12, 0),
        dt.datetime(2026, 4, 1, 0, 0),
        dt.datetime(2027, 1, 1, 12, 0),
    )
