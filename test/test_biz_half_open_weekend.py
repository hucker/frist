"""Half-open interval membership tests for windows spanning a weekend.

Verifies the five-case boundary coverage (below-lower, on-lower,
interior, on-upper, above-upper) for `in_business_days` and
`in_working_days` when the window crosses a weekend.
"""

import datetime as dt
import pytest

from frist import Biz, BizPolicy


def test_biz_half_open_weekend_span_five_cases():
    """Five-case coverage for a business-day window that spans a weekend.

    Use a reference `ref` on Monday 2025-06-09. With default policy
    (Mon-Fri workdays), start=-1 should be Friday 2025-06-06 and end=1
    should be Tuesday 2025-06-10. We assert the five canonical positions
    relative to the business-day window for both business and working days.
    """

    ref: dt.datetime = dt.datetime(2025, 6, 9, 12, 0)  # Monday noon
    policy: BizPolicy = BizPolicy()

    # Arrange: Use known calendar dates for the week around the reference
    # so tests rely only on the public API. With ref on Monday 2025-06-09:
    #   - lower (start=-1) is Friday 2025-06-06
    #   - upper (end=1) is Tuesday 2025-06-10
    lower: dt.date = dt.date(2025, 6, 6)
    upper: dt.date = dt.date(2025, 6, 10)

    dt_below_lower: dt.datetime = dt.datetime.combine(dt.date(2025, 6, 5), dt.time(12, 0))
    dt_on_lower: dt.datetime = dt.datetime.combine(lower, dt.time(12, 0))
    dt_above_lower: dt.datetime = dt.datetime.combine(dt.date(2025, 6, 9), dt.time(12, 0))
    dt_on_upper: dt.datetime = dt.datetime.combine(upper, dt.time(12, 0))
    dt_above_upper: dt.datetime = dt.datetime.combine(dt.date(2025, 6, 11), dt.time(12, 0))

    # business-days (excludes holidays)
    # Act
    def b_biz(t: dt.datetime) -> bool:
        return Biz(t, ref, policy).bday.in_(-1, 1)

    # Assert
    assert b_biz(dt_below_lower) is False, "below lower should be outside business window"
    assert b_biz(dt_on_lower) is True, "on lower should be inside business window"
    assert b_biz(dt_above_lower) is True, "interior day should be inside business window"
    assert b_biz(dt_on_upper) is False, "on upper should be excluded (half-open)"
    assert b_biz(dt_above_upper) is False, "above upper should be outside business window"

    # working-days (ignores holidays)
    # Act
    def b_work(t: dt.datetime) -> bool:
        return Biz(t, ref, policy).wday.in_(-1, 1)

    # Assert
    assert b_work(dt_below_lower) is False, "below lower should be outside working window"
    assert b_work(dt_on_lower) is True, "on lower should be inside working window"
    assert b_work(dt_above_lower) is True, "interior day should be inside working window"
    assert b_work(dt_on_upper) is False, "on upper should be excluded (half-open)"
    assert b_work(dt_above_upper) is False, "above upper should be outside working window"
