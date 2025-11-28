"""Tests for Biz half-open membership semantics.

This module verifies that `Biz.in_business_days` and
`Biz.in_working_days` implement half-open interval semantics
([start, end)) and exercises the five canonical boundary cases
(below-lower, on-lower, interior, on-upper, above-upper).
"""

import datetime as dt
from typing import Callable

from frist import Biz, BizPolicy


def _make_dt(d: dt.date) -> dt.datetime:
  """Return a noon datetime for a given date.

  Args:
    d: Date to convert.

  Returns:
    A datetime at 12:00 on the given date.
  """
  return dt.datetime.combine(d, dt.time(12, 0))


def test_biz_in_business_and_working_days_half_open_five_cases() -> None:
  """Verify Biz in_business_days and in_working_days follow half-open semantics.

  Arrange: choose a reference mid-week so workdays are contiguous around it.
  Act: evaluate `in_business_days` and `in_working_days` for five canonical
  positions relative to the window `start=-1, end=1`.
  Assert: membership matches half-open semantics.
  """

  # Arrange
  ref: dt.datetime = dt.datetime(2025, 1, 15, 12, 0)  # Wednesday
  policy: BizPolicy = BizPolicy()  # default Mon-Fri workdays, no holidays

  # Known dates for the window (start=-1 -> 2025-01-14, end=1 -> 2025-01-16)
  lower: dt.date = dt.date(2025, 1, 14)
  upper: dt.date = dt.date(2025, 1, 16)

  dt_below_lower: dt.datetime = _make_dt(lower - dt.timedelta(days=1))
  dt_on_lower: dt.datetime = _make_dt(lower)
  dt_above_lower: dt.datetime = _make_dt(dt.date(2025, 1, 15))
  dt_on_upper: dt.datetime = _make_dt(upper)
  dt_above_upper: dt.datetime = _make_dt(upper + dt.timedelta(days=1))

  # Act
  # -- business days (excludes holidays)
  b_biz: Callable[[dt.datetime], bool] = lambda t: Biz(t, ref, policy).bday.in_(-1, 1)

  # Assert
  assert b_biz(dt_below_lower) is False, "below lower should be outside business window"
  assert b_biz(dt_on_lower) is True, "on lower should be inside business window"
  assert b_biz(dt_above_lower) is True, "interior day should be inside business window"
  assert b_biz(dt_on_upper) is False, "on upper should be excluded (half-open)"
  assert b_biz(dt_above_upper) is False, "above upper should be outside business window"

  # Act
  # -- working days (ignores holidays)
  b_work: Callable[[dt.datetime], bool] = lambda t: Biz(t, ref, policy).wday.in_(-1, 1)

  # Assert
  assert b_work(dt_below_lower) is False, "below lower should be outside working window"
  assert b_work(dt_on_lower) is True, "on lower should be inside working window"
  assert b_work(dt_above_lower) is True, "interior day should be inside working window"
  assert b_work(dt_on_upper) is False, "on upper should be excluded (half-open)"
  assert b_work(dt_above_upper) is False, "above upper should be outside working window"
