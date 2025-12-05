"""
Business-day unit adapter for `Biz`.

Implements `.in_(offset)` range checks for policy-aware business days (workday
and not holiday) using the provided policy. Does not delegate back to `Biz`.
"""
from __future__ import annotations

import datetime as dt

from .._util import in_half_open_date
from .._biz_policy import BizPolicy
from ._base import CalProtocol, UnitName

class BizDayUnit(UnitName[CalProtocol]):
    """Business day-specific unit using the supplied Biz policy."""

    def __init__(self, cal: CalProtocol, policy: BizPolicy) -> None:
        super().__init__(cal)
        self._policy = policy

    def _move_n_days(self, start_date: dt.date, n: int) -> dt.date:
        if n == 0:
            return start_date
        step = 1 if n > 0 else -1
        remaining = abs(n)
        current = start_date
        while remaining > 0:
            current = current + dt.timedelta(days=step)
            if self._policy.is_business_day(current):
                remaining -= 1
        return current

    def _in_impl(self, start: int, end: int) -> bool:
        ref = self._cal.ref_dt.date()
        tgt = self._cal.target_dt.date()
        if not self._policy.is_business_day(tgt):
            return False
        start_date = self._move_n_days(ref, start)
        end_date = self._move_n_days(ref, end)
        return in_half_open_date(start_date, tgt, end_date)
