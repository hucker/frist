"""Tests for multi-day spans that include weekends.

These tests verify fractional `business_days` and `working_days` when
intervals cross weekend boundaries (e.g., Friday -> Monday). They use
explicit dates and assert expected fractional sums.
"""

import datetime as dt
import pytest

from frist import Biz, BizPolicy


def test_business_and_working_days_span_weekend() -> None:
    """Span Friday morning -> Monday afternoon across a weekend and assert fractional days.

    Arrange: choose a Friday morning target and Monday afternoon ref so the
    span includes two partial business days separated by a weekend.
    Act: compute `business_days` and `working_days`.
    Assert: the fractional sum matches manual inspection (1.625).
    """

    # Arrange
    target: dt.datetime = dt.datetime(2025, 6, 6, 10, 0)  # Friday 2025-06-06 10:00
    ref: dt.datetime = dt.datetime(2025, 6, 9, 15, 0)     # Monday 2025-06-09 15:00

    policy: BizPolicy = BizPolicy()  # defaults: Mon-Fri workdays, 09:00-17:00

    # Act
    b: Biz = Biz(target, ref, policy)

    # Expected by manual inspection: Friday 7/8 + Monday 6/8
    expected: float = 0.875 + 0.75

    # Assert
    assert b.business_days == pytest.approx(expected), f"business_days {b.business_days} != expected {expected}"
    assert b.working_days == pytest.approx(expected), f"working_days {b.working_days} != expected {expected}"
