"""
Business-day unit adapter for `Biz`.

Implements `.in_(offset)` range checks for policy-aware business days (workday
and not holiday) using the provided policy. Does not delegate back to `Biz`.
"""
from __future__ import annotations

import datetime as dt

from .._biz_policy import BizPolicy
from .._util import in_half_open_date
from ._base import CalProtocol
from ._day import DayUnit


class BizDayUnit(DayUnit):
    """Business day unit (inherits Day metadata).

    - Inherits `val` (ISO weekday 1..7) and `name` (weekday string) from `DayUnit`.
    - Provides policy-aware window checks via `in_(start, end)` using business-day stepping.
    - Shortcut: `is_today` only. Use explicit windows with `in_` for previous/next business days.
    """

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
            if self._policy.is_business_day(current):
                remaining -= 1
        return current

    def _in_impl(self, start: int, end: int) -> bool:
        ref = self._cal.ref_dt.date()
        tgt = self._cal.target_dt.date()
        if not self._policy.is_business_day(tgt):
            return False
        start_date = self.move_n_days(ref, start)
        end_date = self.move_n_days(ref, end)
        return in_half_open_date(start_date, tgt, end_date)

    @property
    def is_today(self) -> bool:
        """Return True if current time is within today's business day.

        Alias for `biz_day.in_(0)`. For prior/next windows, prefer
        explicit `in_(start, end)` calls (e.g., `in_(-1, 0)`, `in_(1, 2)`).
        """
        return self.in_(0)

    @property
    def is_yesterday(self) -> bool:
        """Unsupported on business days: raises ValueError.

        Business calendars skip weekends/holidays; "yesterday" is ambiguous.
        Use explicit windows via `in_(start, end)` such as `in_(-1, 0)`.
        """
        raise ValueError("biz_day.is_yesterday is not supported; use in_(-1, 0)")

    @property
    def is_tomorrow(self) -> bool:
        """Unsupported on business days: raises ValueError.

        Business calendars skip weekends/holidays; "tomorrow" is ambiguous.
        Use explicit windows via `in_(start, end)` such as `in_(1, 2)`.
        """
        raise ValueError("biz_day.is_tomorrow is not supported; use in_(1, 2)")

    # Intentionally no is_yesterday/is_tomorrow for business days

    def business_days(self) -> float:
        """Fractional business days between target_dt and ref_dt per policy.

        Uses policy.business_day_fraction which returns 0.0 for holidays.
        """
        if self._cal.target_dt > self._cal.ref_dt:
            raise ValueError(f"{self._cal.target_dt=} must not be after {self._cal.ref_dt=}")

        policy = self._policy
        current = self._cal.target_dt
        end = self._cal.ref_dt
        total = 0.0

        def frac_at(dt_obj: dt.datetime) -> float:
            return policy.business_day_fraction(dt_obj)

        while current.date() <= end.date():
            if policy.is_business_day(current):
                if current.date() == self._cal.target_dt.date():
                    start_dt = self._cal.target_dt
                    end_dt = min(end, dt.datetime.combine(current.date(), policy.end_of_business))
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = end
                else:
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = dt.datetime.combine(current.date(), policy.end_of_business)
                total += max(frac_at(end_dt) - frac_at(start_dt), 0.0)
            current = current + dt.timedelta(days=1)
        return total

    # val and name inherited from DayUnit
