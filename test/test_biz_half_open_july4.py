"""Holiday-aware half-open membership tests (example: July 4).

This module verifies behavior when a window would include a holiday
that should be excluded from `business_days` but still counted for
`working_days`. Tests exercise the five canonical positions around
the window and use explicit dates for clarity.
"""

import datetime as dt
import pytest

from frist import Biz, BizPolicy


def test_biz_half_open_with_july4_holiday():
    """Window that would include July 4 (holiday) should exclude it for business days.

    Reference `ref` is Monday 2025-07-07 noon. With default workdays and a
    policy holiday at 2025-07-04 (Friday):
      - start=-1 -> Friday 2025-07-04 (holiday)
      - end=1   -> Tuesday 2025-07-08

    Expectations (five-case):
      - below lower -> False
      - on lower (holiday) -> business: False, working: True
      - interior (Mon 2025-07-07) -> True for both
      - on upper -> False (exclusive)
      - above upper -> False
    """

    ref = dt.datetime(2025, 7, 7, 12, 0)  # Monday noon

    # Policy with July 4, 2025 marked as a holiday
    policy = BizPolicy(holidays={"2025-07-04"})

    # Because July 4 is a holiday, moving -1 business day from Monday
    # will skip Friday and land on Thursday (2025-07-03). Use explicit
    # dates for clarity.
    dt_below_lower = dt.datetime(2025, 7, 2, 12, 0)   # Wed 2025-07-02
    dt_on_lower = dt.datetime(2025, 7, 3, 12, 0)      # Thu (window start)
    dt_holiday = dt.datetime(2025, 7, 4, 12, 0)       # Fri (holiday)
    dt_interior = dt.datetime(2025, 7, 7, 12, 0)      # Mon (ref)
    dt_on_upper = dt.datetime(2025, 7, 8, 12, 0)      # Tue (exclusive)
    dt_above_upper = dt.datetime(2025, 7, 9, 12, 0)   # Wed

    # business-days (excludes holidays)
    def b_biz(t: dt.datetime) -> bool:
      return Biz(t, ref, policy).bday.in_(-1, 1)

    assert b_biz(dt_below_lower) is False
    assert b_biz(dt_on_lower) is True
    # The holiday itself is not a business day
    assert b_biz(dt_holiday) is False
    assert b_biz(dt_interior) is True
    assert b_biz(dt_on_upper) is False
    assert b_biz(dt_above_upper) is False

    # working-days (ignores holidays)
    def b_work(t: dt.datetime) -> bool:
      return Biz(t, ref, policy).wday.in_(-1, 1)

    assert b_work(dt_below_lower) is False
    # For working-days the start=-1 window lands on Friday (07-04),
    # so Thursday (07-03) is outside that window.
    assert b_work(dt_on_lower) is False
    # The holiday is still a weekday and counts for working-days
    assert b_work(dt_holiday) is True
    assert b_work(dt_interior) is True
    assert b_work(dt_on_upper) is False
    assert b_work(dt_above_upper) is False
