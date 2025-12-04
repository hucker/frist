"""Tests for Biz shortcut properties.

"""

import datetime as dt

from frist import Biz, BizPolicy


def test_is_business_and_workday_next_day_shortcuts():
    """Assert next-day shortcut properties delegate to the `in_*` methods.

    Arrange: create a `BizPolicy` with Mon-Fri workdays and pick Thu/Fri
    as reference/target.
    """
    # Arrange
    policy = BizPolicy()
    ref = dt.datetime(2025, 11, 20, 10, 0)  # Thursday
    target = dt.datetime(2025, 11, 21, 10, 0)  # Friday
    b = Biz(target, ref, policy)

    # Act / Assert
    assert b.is_business_next_day is True, "is_business_next_day should be True for Fri when ref is Thu"
    assert b.is_business_next_day == b.biz_day.in_(1), "business shortcut should equal in_business_days(1)"

    assert b.is_workday_next_day is True, "is_workday_next_day should be True for Fri when ref is Thu"
    assert b.is_workday_next_day == b.work_day.in_(1), "workday shortcut should equal in_working_days(1)"


def test_is_next_fiscal_quarter_and_year_shortcuts():
    """Assert fiscal-quarter/year next shortcuts delegate correctly.

    Uses calendar fiscal-year defaults (fy_start_month=1) so Q1->Q2 and year
    boundary cases are straightforward to construct.
    """
    # Arrange / Act - quarter boundary
    ref = dt.datetime(2025, 3, 15, 12, 0)
    target_q = dt.datetime(2025, 4, 10, 12, 0)
    bq = Biz(target_q, ref, BizPolicy())
    assert bq.is_next_fiscal_quarter is True, "is_next_fiscal_quarter should be True for Apr when ref is Mar"
    assert bq.is_next_fiscal_quarter == bq.fis_qtr.in_(1), "fiscal quarter shortcut mismatch"

    # Arrange / Act - year boundary
    ref_y = dt.datetime(2025, 12, 31, 12, 0)
    target_y = dt.datetime(2026, 1, 1, 12, 0)
    by = Biz(target_y, ref_y, BizPolicy())
    assert by.is_next_fiscal_year is True, "is_next_fiscal_year should be True across year boundary"
    assert by.is_next_fiscal_year == by.fis_year.in_(1), "fiscal year shortcut mismatch"
