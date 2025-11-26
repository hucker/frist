"""Public-API tests for Biz covering edge branches.

These tests follow the repository CODESTYLE: module-level docstring, AAA
(Arrange/Act/Assert) structure, and explicit assert messages to make failures
clear during CI runs.
"""

import datetime as dt
import pytest

from frist import Biz, BizPolicy


def test_working_days_fraction_edges_via_public_api():
    """Verify fractional `working_days` covers business-hour edge cases.

    Arrange: a default `BizPolicy` (Mon-Fri, 9-17).
    Act/Assert: check same-day start/end and a two-business-day span.
    """
    # Arrange
    policy = BizPolicy()  # defaults: workdays Mon-Fri, 9-17

    # Act / Assert - Case A: same calendar day, exactly business start -> 1.0
    target = dt.datetime(2025, 11, 21, 9, 0)
    ref = dt.datetime(2025, 11, 21, 17, 0)
    b = Biz(target, ref, policy)
    assert b.working_days == pytest.approx(1.0), "working_days should be 1.0 for full business day (start->end)"

    # Act / Assert - Case B: same calendar day, at/after business end -> 0.0
    target = dt.datetime(2025, 11, 21, 17, 0)
    ref = dt.datetime(2025, 11, 21, 20, 0)
    b = Biz(target, ref, policy)
    assert b.working_days == pytest.approx(0.0), "working_days should be 0.0 when target at/after business end"

    # Act / Assert - Case C: span across two consecutive business days (Thu -> Fri)
    target = dt.datetime(2025, 11, 20, 12, 0)  # Thursday
    ref = dt.datetime(2025, 11, 21, 12, 0)     # Friday
    b = Biz(target, ref, policy)
    assert b.working_days == pytest.approx(1.0, rel=1e-3), "working_days spanning two business days should total ~1.0"


def test_age_days_helper_raises_value_error_via_public_api():
    """Calling `business_days` with target after ref should raise ValueError.

    This exercises the guard in the internal `_age_days_helper` via the public
    `business_days` property.
    """
    # Arrange
    policy = BizPolicy()
    target = dt.datetime(2025, 11, 24, 12, 0)
    ref = dt.datetime(2025, 11, 23, 12, 0)
    b = Biz(target, ref, policy)

    # Act / Assert
    with pytest.raises(ValueError):
        _ = b.business_days  # expecting ValueError when target_time > ref_time


def test_move_n_days_n_zero_and_early_returns_via_public_api():
    """Verify `in_business_days`/`in_working_days` early returns and n==0 behavior.

    Arrange: create a policy with a single holiday and a policy without holidays.
    Act/Assert: n==0 returns True for business/workday; holiday and weekend return False.
    """
    # Arrange
    policy = BizPolicy(holidays={"2025-11-21"})
    pol2 = BizPolicy(holidays=set())

    # Act / Assert - n == 0 path: target == ref and is a work/business day
    target = dt.datetime(2025, 11, 20, 10, 0)  # Thursday (workday)
    ref = dt.datetime(2025, 11, 20, 10, 0)
    b = Biz(target, ref, pol2)
    assert b.in_business_days(0) is True, "in_business_days(0) should be True when target==ref and not a holiday"
    assert b.in_working_days(0) is True, "in_working_days(0) should be True when target==ref and is a workday"

    # Act / Assert - business_days False when target is a holiday
    target_hol = dt.datetime(2025, 11, 21, 10, 0)
    ref_hol = dt.datetime(2025, 11, 21, 10, 0)
    b_hol = Biz(target_hol, ref_hol, policy)
    assert b_hol.in_business_days(0) is False, "in_business_days(0) should be False for a holiday target"

    # Act / Assert - working_days False when target is not a workday (weekend)
    target_weekend = dt.datetime(2025, 11, 23, 10, 0)
    ref_weekend = dt.datetime(2025, 11, 23, 10, 0)
    b_weekend = Biz(target_weekend, ref_weekend, pol2)
    assert b_weekend.in_working_days(0) is False, "in_working_days(0) should be False for weekend target"
