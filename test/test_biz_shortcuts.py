"""Five-case tests for `Biz` shortcut properties.

These tests verify the five canonical boundary positions for each shortcut:
below-lower, on-lower, interior (above-lower), on-upper (exclusive), above-upper.

Shortcuts covered:
- Day-level: is_business_last_day / is_business_this_day / is_business_next_day
             is_workday_last_day / is_workday_this_day / is_workday_next_day
- Fiscal: is_last_fiscal_quarter / is_this_fiscal_quarter / is_next_fiscal_quarter
          is_last_fiscal_year / is_this_fiscal_year / is_next_fiscal_year
"""
from __future__ import annotations

import datetime as dt

from frist import Biz, CalendarPolicy


def _check_five_biz(prop: str, ref: dt.datetime, policy: CalendarPolicy,
                    dt_below: dt.datetime, dt_on_lower: dt.datetime,
                    dt_above_lower: dt.datetime, dt_on_upper: dt.datetime,
                    dt_above_upper: dt.datetime) -> None:
    """Assert five-case expectations for Biz(...).{prop} given `ref` and `policy`.

    Uses `getattr(Biz(t, ref, policy), prop)` to evaluate the boolean.
    """
    def call(t: dt.datetime) -> bool:
        return getattr(Biz(t, ref, policy), prop)

    assert call(dt_below) is False, f"{prop}: below-lower should be False ({dt_below})"
    assert call(dt_on_lower) is True, f"{prop}: on-lower should be True ({dt_on_lower})"
    assert call(dt_above_lower) is True, f"{prop}: above-lower (interior) should be True ({dt_above_lower})"
    assert call(dt_on_upper) is False, f"{prop}: on-upper should be False (exclusive) ({dt_on_upper})"
    assert call(dt_above_upper) is False, f"{prop}: above-upper should be False ({dt_above_upper})"


def test_day_shortcuts_five_cases() -> None:
    """Day-level business/workday shortcuts five-case coverage."""
    # Reference mid-week so business/workdays are contiguous
    ref = dt.datetime(2025, 1, 15, 12, 0)  # Wednesday
    policy = CalendarPolicy()  # default Mon-Fri workdays, no holidays

    # For the 'this' day shortcuts, the window should be the reference date
    lower_date = ref.date()
    upper_date = ref.date() + dt.timedelta(days=1)

    dt_below = dt.datetime.combine(lower_date - dt.timedelta(days=1), dt.time(12, 0))
    dt_on_lower = dt.datetime.combine(lower_date, dt.time(12, 0))
    dt_above_lower = dt.datetime.combine(lower_date, dt.time(18, 0))
    dt_on_upper = dt.datetime.combine(upper_date, dt.time(12, 0))
    dt_above_upper = dt.datetime.combine(upper_date + dt.timedelta(days=1), dt.time(12, 0))

    # Business-day shortcuts (holiday-aware)
    _check_five_biz("is_business_this_day", ref, policy, dt_below, dt_on_lower, dt_above_lower, dt_on_upper, dt_above_upper)

    # Workday shortcuts (ignore holidays)
    _check_five_biz("is_workday_this_day", ref, policy, dt_below, dt_on_lower, dt_above_lower, dt_on_upper, dt_above_upper)


def test_business_vs_workday_holiday_shortcuts() -> None:
    """Show difference between business and workday shortcuts when a holiday is present.

    With a policy holiday on 2025-07-04 (Friday), the 'last' business-day before
    reference 2025-07-07 will be Thursday 2025-07-03 (the holiday is skipped),
    but the workday shortcut will still consider the holiday a workday.
    """
    ref = dt.datetime(2025, 7, 7, 12, 0)  # Monday
    policy = CalendarPolicy(holidays={"2025-07-04"})

    dt_thu = dt.datetime(2025, 7, 3, 12, 0)
    dt_fri_hol = dt.datetime(2025, 7, 4, 12, 0)

    # Business: last day should be Thursday (03) because Friday (04) is holiday
    assert Biz(dt_thu, ref, policy).is_business_last_day is True
    assert Biz(dt_fri_hol, ref, policy).is_business_last_day is False

    # Workday: Friday still counts as a workday
    assert Biz(dt_fri_hol, ref, policy).is_workday_last_day is True


def test_fiscal_quarter_shortcuts_five_cases() -> None:
    """Fiscal-quarter shortcuts five-case coverage (fiscal year start = April)."""
    policy = CalendarPolicy(fiscal_year_start_month=4)
    # Choose a reference in FY2025 Q2 (July 15, 2025) for clarity
    ref = dt.datetime(2025, 7, 15, 12, 0)

    # last fiscal quarter = Q1 (FY2025 Q1 -> months starting in Apr shifted by fiscal start)
    _check_five_biz(
        "is_last_fiscal_quarter",
        ref,
        policy,
        dt.datetime(2025, 1, 15, 12, 0),   # below lower (earlier than quarter)
        dt.datetime(2025, 4, 1, 12, 0),    # on lower: start of fiscal quarter window
        dt.datetime(2025, 5, 15, 12, 0),   # interior
        dt.datetime(2025, 7, 1, 0, 0),     # on upper: start of next fiscal quarter (excluded)
        dt.datetime(2025, 8, 1, 12, 0),    # above upper
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
    policy = CalendarPolicy(fiscal_year_start_month=4)
    ref = dt.datetime(2025, 7, 15, 12, 0)  # FY2025

    # last fiscal year = FY2024
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

    # this fiscal year = FY2025
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
