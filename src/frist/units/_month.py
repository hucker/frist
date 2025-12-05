"""
Month namespace adapter for `Cal`.

Handles month-aligned half-open windows and related helpers. Internals leverage
calendar boundaries; external recurrence utilities (e.g., `dateutil.rrule`) may
be used by `Cal` for robust month computations.
"""
from __future__ import annotations

import datetime as dt

from dateutil.rrule import FR, MO, MONTHLY, SA, SU, TH, TU, WE, rrule

from ._base import UnitNamespace, CalProtocol
from .._util import in_half_open, normalize_weekday


class MonthNamespace(UnitNamespace[CalProtocol]):
    """Month-specific namespace that implements _in_impl with month logic.

    Migrated from `_ranges.py` to `units/_month.py`.
    """

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _month_index(self, d: dt.datetime) -> int:
        """Get a monotonic month index for comparison."""
        return d.year * 12 + d.month

    def _in_impl(self, start: int, end: int) -> bool:
        """Month-specific logic (moved from cal.in_months)."""
        target_idx: int = self._month_index(self._cal.target_dt)
        start_idx = self._month_index(self._cal.ref_dt) + start
        end_idx = self._month_index(self._cal.ref_dt) + end
        return in_half_open(start_idx, target_idx, end_idx)

    def nth_weekday(self, weekday: str, n: int) -> dt.datetime:
        """
        Get the datetime of the nth occurrence of weekday in ref_dt's month.
        """
        ref_date: dt.date = self._cal.ref_dt.date()
        weekday_num = normalize_weekday(weekday)
        weekday_map = {0: MO, 1: TU, 2: WE, 3: TH, 4: FR, 5: SA, 6: SU}
        rrule_weekday = weekday_map[weekday_num]

        month_start: dt.datetime = dt.datetime(ref_date.year, ref_date.month, 1)
        month_end: dt.datetime = (
            dt.datetime(ref_date.year, ref_date.month + 1, 1)
            - dt.timedelta(days=1)
        )

        rule = rrule(
            MONTHLY,
            byweekday=rrule_weekday,
            bysetpos=n,
            dtstart=month_start,
            until=month_end,
        )
        occurrences = list(rule)
        if not occurrences:
            raise ValueError(f"No {n}th {weekday} in {ref_date.year}-{ref_date.month:02d}")
        occurrence = occurrences[0]
        return occurrence.replace(hour=0, minute=0, second=0, microsecond=0)

    def is_nth_weekday(self, weekday: str, n: int) -> bool:
        try:
            nth_datetime = self.nth_weekday(weekday, n)
            return self._cal.target_dt.date() == nth_datetime.date()
        except ValueError:
            return False

    @property
    def val(self) -> int:
        return self._cal.target_dt.month

    @property
    def name(self) -> str:
        return self._cal.target_dt.strftime("%B")

    @property
    def day(self) -> int:
        return self._cal.target_dt.day
