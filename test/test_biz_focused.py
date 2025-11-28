"""Focused tests for Biz behavior (working_days / business_days / range membership).

Conventions:
- Module-level docstring describing intent.
- Tests follow Arrange / Act / Assert (AAA) via inline comments.
- Use pytest.approx for floating point comparisons.
"""
import datetime as dt
import pytest

from frist import Biz, BizPolicy


def test_multi_day_fraction_working_and_business_days() -> None:
    """Arrange/Act/Assert: fractional working/business days over a multi-day span."""
    # Arrange
    start: dt.datetime = dt.datetime(2024, 1, 1, 12, 0)  # Mon Jan 1 12:00
    end: dt.datetime = dt.datetime(2024, 1, 4, 15, 0)    # Thu Jan 4 15:00
    policy: BizPolicy = BizPolicy()  # default 9-17, Mon-Fri
    biz: Biz = Biz(start, end, policy)

    # Expected fractions per day:
    # Jan 1: 12:00-17:00 = 5/8 = 0.625
    # Jan 2: full workday = 1.0
    # Jan 3: full workday = 1.0
    # Jan 4: 09:00-15:00 = 6/8 = 0.75
    expected: float = 0.625 + 1.0 + 1.0 + 0.75

    # Act / Assert
    assert biz.working_days == pytest.approx(expected, rel=1e-9), "working_days multi-day fraction mismatch"
    assert biz.business_days == pytest.approx(expected, rel=1e-9), "business_days multi-day fraction mismatch"


def test_multi_day_with_middle_holiday() -> None:
    """Arrange/Act/Assert: business_days excludes holidays while working_days counts weekdays."""
    # Arrange
    start: dt.datetime = dt.datetime(2024, 1, 1, 12, 0)
    end: dt.datetime = dt.datetime(2024, 1, 4, 15, 0)
    holidays = {"2024-01-03"}
    policy: BizPolicy = BizPolicy(holidays=holidays)
    biz: Biz = Biz(start, end, policy)

    expected_working: float = 0.625 + 1.0 + 1.0 + 0.75
    expected_business: float = expected_working - 1.0  # Jan 3 becomes 0.0 for business days

    # Act / Assert
    assert biz.working_days == pytest.approx(expected_working, rel=1e-9), "working_days with middle holiday mismatch"
    assert biz.business_days == pytest.approx(expected_business, rel=1e-9), "business_days with middle holiday mismatch"


def test_in_working_and_business_days_range_with_holiday() -> None:
    """Arrange/Act/Assert: range membership behaves differently for working vs business days with holidays."""
    # Arrange
    ref: dt.datetime = dt.datetime(2024, 1, 4, 12, 0)
    target: dt.datetime = dt.datetime(2024, 1, 2, 10, 0)
    policy: BizPolicy = BizPolicy()
    biz: Biz = Biz(target, ref, policy)

    # Act / Assert - no holiday
    assert biz.wday.in_(-2, 0) is True, "target should be in working_days(-2,0)"
    assert biz.bday.in_(-2, 0) is True, "target should be in business_days(-2,0)"

    # Arrange - make Jan 2 a holiday
    policy2: BizPolicy = BizPolicy(holidays={"2024-01-02"})
    biz2: Biz = Biz(target, ref, policy2)

    # Act / Assert - business-day membership should be False while working-day membership remains True
    assert biz2.wday.in_(-2, 0) is True, "working_days should ignore holiday"
    assert biz2.bday.in_(-2, 0) is False, "business_days should exclude holiday"