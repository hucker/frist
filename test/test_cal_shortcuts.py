"""Tests for `Cal` shortcut properties (is_today, is_yesterday, is_tomorrow,
is_last_week/is_this_week/is_next_week, is_last_month/is_this_month/is_next_month,
is_last_quarter/is_this_quarter/is_next_quarter, is_last_year/is_this_year/is_next_year).

Each shortcut is a thin wrapper around an `in_*` method and should follow
half-open semantics. These tests exercise the five canonical boundary cases:
below-lower, on-lower, interior (above-lower), on-upper (exclusive), above-upper.
"""
from __future__ import annotations

import datetime as dt

import pytest

from frist import Cal


def _check_five(prop: str, ref: dt.datetime, dt_below: dt.datetime, dt_on_lower: dt.datetime,
                dt_above_lower: dt.datetime, dt_on_upper: dt.datetime, dt_above_upper: dt.datetime) -> None:
    """Helper: assert five-case expectations for Cal(...).{prop} given `ref`.

    The helper calls `getattr(Cal(t, ref), prop)` for each datetime and asserts
    the expected boolean membership for the five positions.
    """
    def call(t: dt.datetime) -> bool:
        return getattr(Cal(t, ref), prop)

    assert call(dt_below) is False, f"{prop}: below-lower should be False ({dt_below})"
    assert call(dt_on_lower) is True, f"{prop}: on-lower should be True ({dt_on_lower})"
    assert call(dt_above_lower) is True, f"{prop}: above-lower (interior) should be True ({dt_above_lower})"
    assert call(dt_on_upper) is False, f"{prop}: on-upper should be False (exclusive) ({dt_on_upper})"
    assert call(dt_above_upper) is False, f"{prop}: above-upper should be False ({dt_above_upper})"


def test_day_shortcuts_five_cases():
    """Day-based shortcuts: is_today, is_yesterday, is_tomorrow."""
    ref = dt.datetime(2025, 6, 9, 12, 0)  # Monday noon

    # is_today -> in_days(0): window is 2025-06-09 .. 2025-06-10
    _check_five(
        "is_today",
        ref,
        dt.datetime(2025, 6, 8, 12, 0),   # below lower: Sunday
        dt.datetime(2025, 6, 9, 12, 0),   # on lower: Monday (today)
        dt.datetime(2025, 6, 9, 18, 0),   # interior: later Monday
        dt.datetime(2025, 6, 10, 12, 0),  # on upper: Tuesday noon (excluded)
        dt.datetime(2025, 6, 11, 12, 0),  # above upper: Wednesday
    )

    # is_yesterday -> in_days(-1): window is 2025-06-08 .. 2025-06-09
    _check_five(
        "is_yesterday",
        ref,
        dt.datetime(2025, 6, 7, 12, 0),   # below lower
        dt.datetime(2025, 6, 8, 12, 0),   # on lower
        dt.datetime(2025, 6, 8, 23, 59),  # interior
        dt.datetime(2025, 6, 9, 0, 0),    # on upper: start of today (excluded)
        dt.datetime(2025, 6, 9, 12, 0),   # above upper
    )

    # is_tomorrow -> in_days(1): window is 2025-06-10 .. 2025-06-11
    _check_five(
        "is_tomorrow",
        ref,
        dt.datetime(2025, 6, 9, 0, 0),    # below lower: today start
        dt.datetime(2025, 6, 10, 9, 0),   # on lower: tomorrow
        dt.datetime(2025, 6, 10, 23, 59), # interior: later tomorrow
        dt.datetime(2025, 6, 11, 0, 0),   # on upper: day after tomorrow (excluded)
        dt.datetime(2025, 6, 12, 12, 0),  # above upper
    )


def test_week_shortcuts_five_cases():
    """Week-based shortcuts: last/this/next week (Monday-start window)."""
    ref = dt.datetime(2025, 6, 9, 12, 0)  # Monday noon

    # last week window: 2025-06-02 .. 2025-06-09
    _check_five(
        "is_last_week",
        ref,
        dt.datetime(2025, 5, 31, 12, 0),   # below lower
        dt.datetime(2025, 6, 2, 12, 0),    # on lower: Monday of last week
        dt.datetime(2025, 6, 4, 12, 0),    # interior
        dt.datetime(2025, 6, 9, 0, 0),     # on upper: Monday of current week (excluded)
        dt.datetime(2025, 6, 16, 12, 0),   # above upper
    )

    # this week window: 2025-06-09 .. 2025-06-16
    _check_five(
        "is_this_week",
        ref,
        dt.datetime(2025, 6, 8, 12, 0),    # below lower
        dt.datetime(2025, 6, 9, 12, 0),    # on lower
        dt.datetime(2025, 6, 11, 12, 0),   # interior
        dt.datetime(2025, 6, 16, 0, 0),    # on upper (excluded)
        dt.datetime(2025, 6, 17, 12, 0),   # above upper
    )

    # next week window: 2025-06-16 .. 2025-06-23
    _check_five(
        "is_next_week",
        ref,
        dt.datetime(2025, 6, 15, 12, 0),   # below lower
        dt.datetime(2025, 6, 16, 9, 0),    # on lower
        dt.datetime(2025, 6, 18, 12, 0),   # interior
        dt.datetime(2025, 6, 23, 0, 0),    # on upper (excluded)
        dt.datetime(2025, 6, 24, 12, 0),   # above upper
    )


def test_month_shortcuts_five_cases():
    """Month-based shortcuts: last/this/next month (calendar-month aligned)."""
    ref = dt.datetime(2025, 6, 15, 12, 0)  # mid-June

    # last month = May 2025
    _check_five(
        "is_last_month",
        ref,
        dt.datetime(2025, 4, 15, 12, 0),   # below lower
        dt.datetime(2025, 5, 1, 12, 0),    # on lower
        dt.datetime(2025, 5, 20, 12, 0),   # interior
        dt.datetime(2025, 6, 1, 0, 0),     # on upper (excluded)
        dt.datetime(2025, 7, 2, 12, 0),    # above upper
    )

    # this month = June 2025
    _check_five(
        "is_this_month",
        ref,
        dt.datetime(2025, 5, 31, 23, 59),  # below lower
        dt.datetime(2025, 6, 1, 12, 0),    # on lower
        dt.datetime(2025, 6, 20, 12, 0),   # interior
        dt.datetime(2025, 7, 1, 0, 0),     # on upper (excluded)
        dt.datetime(2025, 8, 1, 12, 0),    # above upper
    )

    # next month = July 2025
    _check_five(
        "is_next_month",
        ref,
        dt.datetime(2025, 6, 30, 23, 59),  # below lower
        dt.datetime(2025, 7, 1, 9, 0),     # on lower
        dt.datetime(2025, 7, 10, 12, 0),   # interior
        dt.datetime(2025, 8, 1, 0, 0),     # on upper (excluded)
        dt.datetime(2025, 9, 1, 12, 0),    # above upper
    )


def test_quarter_shortcuts_five_cases():
    """Quarter-based shortcuts: last/this/next quarter (calendar-aligned)."""
    ref = dt.datetime(2025, 5, 15, 12, 0)  # Q2

    # last quarter = Q1 (Jan-Mar 2025)
    _check_five(
        "is_last_quarter",
        ref,
        dt.datetime(2024, 12, 15, 12, 0),  # below lower
        dt.datetime(2025, 1, 15, 12, 0),   # on lower
        dt.datetime(2025, 3, 31, 12, 0),   # interior
        dt.datetime(2025, 4, 1, 0, 0),     # on upper (excluded)
        dt.datetime(2025, 5, 15, 12, 0),   # above upper
    )

    # this quarter = Q2 (Apr-Jun 2025)
    _check_five(
        "is_this_quarter",
        ref,
        dt.datetime(2025, 3, 31, 23, 59),  # below lower
        dt.datetime(2025, 4, 1, 12, 0),    # on lower
        dt.datetime(2025, 5, 30, 12, 0),   # interior
        dt.datetime(2025, 7, 1, 0, 0),     # on upper (excluded)
        dt.datetime(2025, 8, 1, 12, 0),    # above upper
    )

    # next quarter = Q3 (Jul-Sep 2025)
    _check_five(
        "is_next_quarter",
        ref,
        dt.datetime(2025, 6, 30, 12, 0),   # below lower
        dt.datetime(2025, 7, 1, 9, 0),     # on lower
        dt.datetime(2025, 8, 15, 12, 0),   # interior
        dt.datetime(2025, 10, 1, 0, 0),    # on upper (excluded)
        dt.datetime(2026, 1, 15, 12, 0),   # above upper
    )


def test_year_shortcuts_five_cases():
    """Year-based shortcuts: last/this/next year."""
    ref = dt.datetime(2025, 6, 15, 12, 0)

    # last year = 2024
    _check_five(
        "is_last_year",
        ref,
        dt.datetime(2023, 12, 31, 12, 0),  # below lower
        dt.datetime(2024, 6, 15, 12, 0),   # on lower
        dt.datetime(2024, 12, 31, 12, 0),  # interior
        dt.datetime(2025, 1, 1, 0, 0),     # on upper (excluded)
        dt.datetime(2026, 3, 1, 12, 0),    # above upper
    )

    # this year = 2025
    _check_five(
        "is_this_year",
        ref,
        dt.datetime(2024, 12, 31, 23, 59),  # below lower
        dt.datetime(2025, 1, 1, 0, 0),      # on lower
        dt.datetime(2025, 10, 1, 12, 0),    # interior
        dt.datetime(2026, 1, 1, 0, 0),      # on upper (excluded)
        dt.datetime(2027, 1, 1, 0, 0),      # above upper
    )

    # next year = 2026
    _check_five(
        "is_next_year",
        ref,
        dt.datetime(2024, 12, 31, 23, 59),  # below lower
        dt.datetime(2026, 1, 1, 0, 0),      # on lower
        dt.datetime(2026, 6, 1, 12, 0),     # interior
        dt.datetime(2027, 1, 1, 0, 0),      # on upper (excluded)
        dt.datetime(2028, 1, 1, 0, 0),      # above upper
    )
