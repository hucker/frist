"""
Working-day unit adapter for `Biz`.

Provides `.in_(offset)` for policy-defined workdays (ignores holidays). Range
logic implemented here using the provided policy.
"""
from __future__ import annotations

import datetime as dt

from .._biz_policy import BizPolicy
from .._util import in_half_open_date
from ._base import CalProtocol
from ._day import DayUnit


class WorkingDayUnit(DayUnit):
    """Working day unit (inherits Day metadata).

    - Inherits `val` (ISO weekday 1..7) and `name` (weekday string) from `DayUnit`.
    - Provides policy-aware window checks via `in_(start, end)` using working-day stepping.
    - Shortcut: `is_today` only. Use explicit windows with `in_` for previous/next working days.
    """

    def __init__(self, cal: CalProtocol, policy: BizPolicy) -> None:
        super().__init__(cal)
        self._policy = policy

    def move_n_days(self, start_date: dt.date, n: int) -> dt.date:
        """
        Move forward or backward by `n` working days from `start_date` using the policy.

        Behavior:
        - Steps one calendar day at a time in the sign of `n` (+ → forward, - → backward).
        - Counts only days where `policy.is_workday(date)` is True.
        - Returns `start_date` immediately when `n == 0`.
        - This assumes that workdays may be non-contiguous.

        Args:
            start_date: The starting calendar date.
            n: Number of working days to move. Positive moves forward; negative moves backward.

        Returns:
            A `datetime.date` that is `n` working days away from `start_date` per the policy.

        Examples:
            # Forward 3 working days (skips weekends/non-workdays)
            move_n_days(dt.date(2025, 12, 5), 3)

            # Backward 2 working days
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
        """Signed fractional working days between target_dt and ref_dt per policy.

        Positive when `target_dt <= ref_dt`, negative when `target_dt > ref_dt`.
        Holidays are ignored (only workdays contribute).
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

        while current.date() <= end.date():
            if policy.is_workday(current):
                if current.date() == start.date():
                    start_dt = start
                    end_dt = min(end, dt.datetime.combine(current.date(), policy.end_of_business))
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = end
                else:
                    start_dt = dt.datetime.combine(current.date(), policy.start_of_business)
                    end_dt = dt.datetime.combine(current.date(), policy.end_of_business)

                total += max(
                    self.workday_fraction_at(end_dt) - self.workday_fraction_at(start_dt),
                    0.0,
                )
            current = current + dt.timedelta(days=1)

        return sign * total

    # val and name inherited from DayUnit

    @property
    def is_today(self) -> bool:
        """Convenience shortcut for same working day as reference.

        Alias for `work_day.in_(0)`. For prior/next windows, prefer
        explicit `in_(start, end)` calls (e.g., `in_(-1, 0)`, `in_(1, 2)`).
        """
        return self.in_(0)

    @property
    def is_yesterday(self) -> bool:
        """Unsupported on working days: weekends/holidays break contiguity.

        Use explicit window checks via `in_(start, end)`, e.g., `in_(-1, 0)`.
        """
        raise ValueError(
            "Unsupported on working days: weekends/holidays break contiguity. "
            "Use explicit window checks via in_(start, end), e.g., in_(-1, 0)."
        )

    @property
    def is_tomorrow(self) -> bool:
        """Unsupported on working days: weekends/holidays break contiguity.

        Use explicit window checks via `in_(start, end)`, e.g., `in_(1, 2)`.
        """
        raise ValueError(
            "Unsupported on working days: weekends/holidays break contiguity. "
            "Use explicit window checks via in_(start, end), e.g., in_(1, 2)."
        )
