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
        """
        Move forward or backward by `n` business days from `start_date` per policy.

        Behavior:
        - Steps one calendar day at a time in the sign of `n` (+ → forward, - → backward).
        - Counts only days where `policy.is_business_day(date)` is True (workday and not a holiday).
        - Returns `start_date` immediately when `n == 0`.
        - Assumes that business days may be non-contiguous and that holidays may fall on workdays.

        Args:
            start_date: The starting calendar date.
            n: Number of business days to move. Positive moves forward; negative moves backward.

        Returns:
            A `datetime.date` that is `n` business days away from `start_date` under the policy.

        Examples:
            # Forward 3 business days (skips weekends and holidays)
            move_n_days(dt.date(2025, 12, 5), 3)

            # Backward 2 business days
            move_n_days(dt.date(2025, 12, 5), -2)

            # No movement
            move_n_days(dt.date(2025, 12, 5), 0)
        """
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
        """Unsupported on business days: weekends/holidays break contiguity.

        Use explicit window checks via `in_(start, end)`, e.g., `in_(-1, 0)`.
        """
        raise ValueError(
            "Unsupported on business days: weekends/holidays break contiguity. "
            "Use explicit window checks via in_(start, end), e.g., in_(-1, 0)."
        )

    @property
    def is_tomorrow(self) -> bool:
        """Unsupported on business days: weekends/holidays break contiguity.

        Use explicit window checks via `in_(start, end)`, e.g., `in_(1, 2)`.
        """
        raise ValueError(
            "Unsupported on business days: weekends/holidays break contiguity. "
            "Use explicit window checks via in_(start, end), e.g., in_(1, 2)."
        )


    def business_days(self) -> float:
        """Signed fractional business days between target_dt and ref_dt per policy.

        Positive when `target_dt <= ref_dt`, negative when `target_dt > ref_dt`.
        Uses policy.business_day_fraction (holidays contribute 0.0).
        """
        policy = self._policy
        start = self._cal.target_dt
        end = self._cal.ref_dt

        if start == end:
            return 0.0

        sign = 1.0
        if start > end:
            start, end = end, start
            sign = -1.0

        total = 0.0
        current = start

        def frac_at(dt_obj: dt.datetime) -> float:
            return policy.business_day_fraction(dt_obj)

        while current.date() <= end.date():
            if policy.is_business_day(current):
                if current.date() == start.date():
                    start_dt = start
                    end_dt = min(end, dt.datetime.combine(current.date(), policy.end_of_business))
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = end
                else:
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = dt.datetime.combine(current.date(), policy.end_of_business)
                total += max(frac_at(end_dt) - frac_at(start_dt), 0.0)
            current = current + dt.timedelta(days=1)

        return sign * total

    # val and name inherited from DayUnit
