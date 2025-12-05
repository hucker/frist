"""
Edge-case tests for Biz behavior.

AAA Pattern:
- Arrange: Construct Biz/BizPolicy with explicit target/ref datetimes.
- Act: Execute the behavior under test.
- Assert: Compare expected vs actual with clear messages.
"""

# pyright: reportPrivateUsage=false

import datetime as dt

import pytest

from frist._biz import Biz
from frist._biz_policy import BizPolicy


def test_workday_fraction_zero_length_business_day() -> None:
    """Zero-length business day yields fraction 0.0 at business start."""
    # Arrange
    policy = BizPolicy(start_of_business=dt.time(9, 0), end_of_business=dt.time(9, 0))
    ref = dt.datetime(2025, 1, 2, 12, 0)
    target = dt.datetime(2025, 1, 2, 9, 0)
    biz = Biz(target_dt=target, ref_dt=ref, policy=policy)

    # Act/Assert
    actual = biz.work_day.workday_fraction_at(target)
    expected = 0.0
    assert actual == expected, (
        f"Workday fraction mismatch: expected={expected}, actual={actual}"
    )


def test_workday_fraction_before_and_after() -> None:
    """Workday fraction is 0.0 before start and 1.0 after end."""
    # Arrange
    policy = BizPolicy(start_of_business=dt.time(9, 0), end_of_business=dt.time(17, 0))
    biz_before = Biz(
        target_dt=dt.datetime(2025, 1, 2, 8, 0),
        ref_dt=dt.datetime(2025, 1, 2, 12, 0),
        policy=policy,
    )
    biz_after = Biz(
        target_dt=dt.datetime(2025, 1, 2, 18, 0),
        ref_dt=dt.datetime(2025, 1, 2, 12, 0),
        policy=policy,
    )

    # Act/Assert
    actual_before = biz_before.work_day.workday_fraction_at(biz_before.target_dt)
    expected_before = 0.0
    assert actual_before == expected_before, (
        f"Workday fraction (before) mismatch: expected={expected_before}, actual={actual_before}"
    )

    actual_after = biz_after.work_day.workday_fraction_at(biz_after.target_dt)
    expected_after = 1.0
    assert actual_after == expected_after, (
        f"Workday fraction (after) mismatch: expected={expected_after}, actual={actual_after}"
    )


def test_age_days_helper_raises_when_target_after_ref() -> None:
    """business_days property raises when target_dt > ref_dt."""
    # Arrange
    ref = dt.datetime(2025, 1, 1, 0, 0)
    target = dt.datetime(2025, 1, 2, 0, 0)  # target > ref
    biz = Biz(target_dt=target, ref_dt=ref)

    # Act/Assert
    with pytest.raises(ValueError):
        _ = biz.business_days


def test_move_n_days_zero_returns_same_date() -> None:
    """Moving zero days returns the same date for business/non-business counts."""
    # Arrange
    policy = BizPolicy()
    biz = Biz(target_dt=dt.datetime(2025, 1, 1), ref_dt=dt.datetime(2025, 1, 1), policy=policy)
    d = dt.date(2025, 1, 10)

    # Act/Assert
    actual_business = biz.biz_day.move_n_days(d, 0)
    actual_calendar = biz.work_day.move_n_days(d, 0)
    expected = d
    assert actual_business == expected, (
        f"Move n days (business) mismatch: expected={expected}, actual={actual_business}"
    )
    assert actual_calendar == expected, (
        f"Move n days (calendar) mismatch: expected={expected}, actual={actual_calendar}"
    )


def test_get_fiscal_year_and_quarter_before_and_after_fy_start() -> None:
    """Fiscal year/quarter reflect month-based fiscal year start (April = 4)."""
    # Arrange
    policy = BizPolicy(fiscal_year_start_month=4)

    # Act/Assert (March -> FY 2024, Q4)
    dt_obj = dt.datetime(2025, 3, 15)
    actual_fy_before = Biz.get_fiscal_year(dt_obj, policy.fiscal_year_start_month)
    actual_fq_before = Biz.get_fiscal_quarter(dt_obj, policy.fiscal_year_start_month)
    assert actual_fy_before == 2024, (
        f"Fiscal year (before) mismatch: expected=2024, actual={actual_fy_before}"
    )
    assert actual_fq_before == 4, (
        f"Fiscal quarter (before) mismatch: expected=4, actual={actual_fq_before}"
    )

    # Act/Assert (April -> FY 2025, Q1)
    dt_obj2 = dt.datetime(2025, 4, 2)
    actual_fy_after = Biz.get_fiscal_year(dt_obj2, policy.fiscal_year_start_month)
    actual_fq_after = Biz.get_fiscal_quarter(dt_obj2, policy.fiscal_year_start_month)
    assert actual_fy_after == 2025, (
        f"Fiscal year (after) mismatch: expected=2025, actual={actual_fy_after}"
    )
    assert actual_fq_after == 1, (
        f"Fiscal quarter (after) mismatch: expected=1, actual={actual_fq_after}"
    )
