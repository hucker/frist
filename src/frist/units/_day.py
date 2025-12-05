"""
Day unit adapter for `Cal`.

Implements ergonomic `.in_(offset)` checks for calendar day half-open windows,
delegating to `Cal` for core behavior.
"""
from __future__ import annotations

import datetime as dt

from ._base import UnitName, CalProtocol
from .._util import in_half_open_date


class DayUnit(UnitName[CalProtocol]):
    """Day-specific unit that implements _in_impl with day logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        """Day-specific logic (moved from cal.in_days)."""

        target_date = self._cal.target_dt.date()

        # Calculate the date range boundaries
        start_date: dt.datetime = (self._cal.ref_dt + dt.timedelta(days=start)).date()
        end_date: dt.datetime = (self._cal.ref_dt + dt.timedelta(days=end)).date()

        return in_half_open_date(start_date, target_date, end_date)

    @property
    def val(self) -> int:
        """
        Returns the day of the week value (1=Mon .. 7=Sun) for the target time.
        """
        return self._cal.target_dt.isoweekday()

    @property
    def name(self) -> str:
        """
        Returns the day name for the target time.
        """
        return self._cal.target_dt.strftime("%A")

    @property
    def is_today(self) -> bool:
        """Convenience shortcut for same calendar day as reference.

        Alias for `day.in_(0)`.
        For other windows, use `day.in_(start, end)`, `day.between(...)`, or `day.thru(...)`.
        """
        return self.in_(0)

    @property
    def is_yesterday(self) -> bool:
        """Convenience shortcut for previous calendar day relative to reference.

        Alias for `day.in_(-1)`.
        For other windows, use `day.in_(start, end)`, `day.between(...)`, or `day.thru(...)`.
        """
        return self.in_(-1)

    @property
    def is_tomorrow(self) -> bool:
        """Convenience shortcut for next calendar day relative to reference.

        Alias for `day.in_(1)`.
        For other windows, use `day.in_(start, end)`, `day.between(...)`, or `day.thru(...)`.
        """
        return self.in_(1)
