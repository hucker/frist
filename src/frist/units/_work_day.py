"""
Working-day unit adapter for `Biz`.

Provides `.in_(offset)` for policy-defined workdays (ignores holidays). Range
logic implemented here using the provided policy.
"""
from __future__ import annotations

import datetime as dt

from .._biz_policy import BizPolicy
from .._util import in_half_open_date
from ._base import CalProtocol, UnitName


class WorkingDayUnit(UnitName[CalProtocol]):
    """Working day-specific unit using the supplied Biz policy."""

    def __init__(self, cal: CalProtocol, policy: BizPolicy) -> None:
        super().__init__(cal)
        self._policy = policy

    def move_n_days(self, start_date: dt.date, n: int) -> dt.date:
        if n == 0:
            return start_date
        step = 1 if n > 0 else -1
        remaining = abs(n)
        current = start_date
        while remaining > 0:
            current = current + dt.timedelta(days=step)
            if self._policy.is_workday(current):
                remaining -= 1
        return current

    def _in_impl(self, start: int, end: int) -> bool:
        ref = self._cal.ref_dt.date()
        tgt = self._cal.target_dt.date()
        if not self._policy.is_workday(tgt):
            return False
        start_date = self.move_n_days(ref, start)
        end_date = self.move_n_days(ref, end)
        return in_half_open_date(start_date, tgt, end_date)

    def workday_fraction_at(self, dt_obj: dt.datetime) -> float:
        """Fraction of working-day elapsed at dt_obj (ignores holidays)."""
        start = self._policy.start_of_business
        end = self._policy.end_of_business
        start_dt = dt.datetime.combine(dt_obj.date(), start)
        end_dt = dt.datetime.combine(dt_obj.date(), end)
        total = (end_dt - start_dt).total_seconds()
        cur = (dt.datetime.combine(dt_obj.date(), dt_obj.time()) - start_dt).total_seconds()
        if cur <= 0:
            return 0.0
        if cur >= total:
            return 1.0
        return cur / total if total > 0 else 0.0

    def working_days(self) -> float:
        """Fractional working days between target_dt and ref_dt per policy."""
        if self._cal.target_dt > self._cal.ref_dt:
            raise ValueError(f"{self._cal.target_dt=} must not be after {self._cal.ref_dt=}")

        policy = self._policy
        current = self._cal.target_dt
        end = self._cal.ref_dt
        total = 0.0

        while current.date() <= end.date():
            if policy.is_workday(current):
                if current.date() == self._cal.target_dt.date():
                    start_dt = self._cal.target_dt
                    end_dt = min(end, dt.datetime.combine(current.date(), policy.end_of_business))
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = end
                else:
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = dt.datetime.combine(current.date(), policy.end_of_business)
                total += max(
                    self.workday_fraction_at(end_dt)
                    - self.workday_fraction_at(start_dt),
                    0.0,
                )
            current = current + dt.timedelta(days=1)
        return total
