"""
Week unit adapter for `Cal`.

Provides `.in_(offset)` checks using calendar-aligned week boundaries (default
start Monday) with half-open semantics. Delegates to `Cal`.
"""
from __future__ import annotations

import datetime as dt

from ._base import UnitName, CalProtocol
from .._util import in_half_open_date, normalize_weekday


class WeekUnit(UnitName[CalProtocol]):
    """Week-specific unit that implements _in_impl with week logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        """Week-specific logic (moved from cal.in_weeks)."""

        week_start_day: int = normalize_weekday("monday")  # default week start

        target_date: dt.date = self._cal.target_dt.date()
        base_date: dt.date = self._cal.ref_dt.date()

        # Calculate the start of the current week based on week_start_day
        days_since_week_start: int = (base_date.weekday() - week_start_day) % 7
        current_week_start: dt.date = base_date - dt.timedelta(days=days_since_week_start)

        # Calculate week boundaries
        start_week_start = current_week_start + dt.timedelta(weeks=start)
        end_week_start = current_week_start + dt.timedelta(weeks=end)
        # Half-open semantics for weeks: `end_week_start` is already the
        # exclusive start-of-week produced by the normalized `end` value;
        # do not add an extra week here.
        end_week_exclusive = end_week_start

        return in_half_open_date(start_week_start, target_date, end_week_exclusive)

    @property
    def val(self) -> int:
        """
        Returns the week value (1-53) for the target time.
        """
        return self._cal.target_dt.isocalendar().week  # type: ignore

    @property
    def day(self) -> int:
        """
        Returns the day of week value (1=Mon .. 7=Sun) for the target time.
        """
        return self._cal.target_dt.isoweekday()
