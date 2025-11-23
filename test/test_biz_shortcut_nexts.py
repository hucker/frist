"""Tests for Biz shortcut properties.

Follow CODESTYLE: module docstring, AAA structure, and explicit assert
messages. These tests exercise the thin shortcut properties that delegate
to `in_*` helpers.
"""

import datetime as dt

from frist import Biz, CalendarPolicy


def test_is_business_and_workday_next_day_shortcuts():
    """Assert next-day shortcut properties delegate to the `in_*` methods.

    Arrange: create a `CalendarPolicy` with Mon-Fri workdays and pick Thu/Fri
    as reference/target.
    """
    # Arrange
    policy = CalendarPolicy()
    ref = dt.datetime(2025, 11, 20, 10, 0)  # Thursday
    target = dt.datetime(2025, 11, 21, 10, 0)  # Friday
    b = Biz(target, ref, policy)

    # Act / Assert
    assert b.is_business_next_day is True, "is_business_next_day should be True for Fri when ref is Thu"
    assert b.is_business_next_day == b.in_business_days(1), "business shortcut should equal in_business_days(1)"

    assert b.is_workday_next_day is True, "is_workday_next_day should be True for Fri when ref is Thu"
    assert b.is_workday_next_day == b.in_working_days(1), "workday shortcut should equal in_working_days(1)"


def test_is_next_fiscal_quarter_and_year_shortcuts():
    """Assert fiscal-quarter/year next shortcuts delegate correctly.

    Uses calendar fiscal-year defaults (fy_start_month=1) so Q1->Q2 and year
    boundary cases are straightforward to construct.
    """
    # Arrange / Act - quarter boundary
    ref = dt.datetime(2025, 3, 15, 12, 0)
    target_q = dt.datetime(2025, 4, 10, 12, 0)
    bq = Biz(target_q, ref, CalendarPolicy())
    assert bq.is_next_fiscal_quarter is True, "is_next_fiscal_quarter should be True for Apr when ref is Mar"
    assert bq.is_next_fiscal_quarter == bq.in_fiscal_quarters(1), "fiscal quarter shortcut mismatch"

    # Arrange / Act - year boundary
    ref_y = dt.datetime(2025, 12, 31, 12, 0)
    target_y = dt.datetime(2026, 1, 1, 12, 0)
    by = Biz(target_y, ref_y, CalendarPolicy())
    assert by.is_next_fiscal_year is True, "is_next_fiscal_year should be True across year boundary"
    assert by.is_next_fiscal_year == by.in_fiscal_years(1), "fiscal year shortcut mismatch"
