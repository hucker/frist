from __future__ import annotations

import datetime as dt

from ._base import UnitNamespace, CalProtocol
from .._util import in_half_open_date


class DayNamespace(UnitNamespace[CalProtocol]):
    """Day-specific namespace that implements _in_impl with day logic.

    Migrated from `_ranges.py` to `units/_day.py`.
    """

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
