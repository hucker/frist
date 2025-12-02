from __future__ import annotations
from typing import Callable, Optional
import datetime as dt
from ._util import in_half_open_date
__all__ = ["UnitNamespace"]


class UnitNamespace:
    """Compact unit namespace that delegates to a Cal `in_*` method.

    Usage examples (compact):
      cal.month.in_(-2, 0)     # half-open (default)
      cal.month(-2, 0)         # maps to in_
      cal.month.thru(-2, 0)    # inclusive end
            # slice syntax is not supported
    """

    def __init__(self, cal: object, fn: Optional[Callable[[int, Optional[int]], bool]] = None) -> None:
        self._cal = cal
        self._fn = fn

    def in_(self, start: int = 0, end: Optional[int] = None) -> bool:
        """Half-open membership: start <= target < end.

        Single-arg (end omitted) -> single-unit window [start, start+1).
        """
        if end is None:
            end = start + 1
        if start >= end:
            raise ValueError(f"{self.__class__.__name__}.in_: start ({start}) must not be greater than end ({end})")
        # Use _in_impl if available (for subclasses), otherwise fall back to _fn
        if hasattr(self, '_in_impl'):
            return self._in_impl(start, end)
        return self._fn(start, end)

    @property
    def between(self):
        """Alias for in_ method."""
        return self.in_

    def __call__(self, start: int = 0, end: Optional[int] = None) -> bool:
        return self.in_(start, end)


    def _thru_impl(self, start: int = 0, end: Optional[int] = None) -> bool:
        # single-arg -> same single unit; convert inclusive -> half-open by +1
        if end is None:
            end = start
        return self.in_(start, end + 1)

    @property
    def thru(self):
        """Return a callable object supporting call syntax for inclusive "through" semantics.

        Example: `cal.month.thru(-2, 0)`.
        """

        parent = self

        class _Thru:
            def __call__(self, s: int = 0, e: Optional[int] = None) -> bool:
                return parent._thru_impl(s, e)

        return _Thru()


class MinuteNamespace(UnitNamespace):
    """Minute-specific namespace that implements _in_impl with minute logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Minute-specific logic (moved from cal.in_minutes)."""
        from ._util import in_half_open_dt

        ref: dt.datetime = self._cal.ref_dt
        target: dt.datetime = self._cal.target_dt

        # compute minute-aligned boundaries
        start_time: dt.datetime = ref + dt.timedelta(minutes=start)
        start_minute:dt.datetime = start_time.replace(second=0, microsecond=0)

        end_time = ref + dt.timedelta(minutes=end)
        end_minute = end_time.replace(second=0, microsecond=0)

        return in_half_open_dt(start_minute, target, end_minute)


class HourNamespace(UnitNamespace):
    """Hour-specific namespace that implements _in_impl with hour logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Hour-specific logic (moved from cal.in_hours)."""
        from ._util import in_half_open_dt

        ref:dt.datetime = self._cal.ref_dt
        target = self._cal.target_dt

        # compute hour-aligned boundaries
        start_time = ref + dt.timedelta(hours=start)
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)

        end_time = ref + dt.timedelta(hours=end)
        end_hour = end_time.replace(minute=0, second=0, microsecond=0)

        return in_half_open_dt(start_hour, target, end_hour)


class DayNamespace(UnitNamespace):
    """Day-specific namespace that implements _in_impl with day logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Day-specific logic (moved from cal.in_days)."""

        target_date = self._cal.target_dt.date()

        # Calculate the date range boundaries
        start_date = (self._cal.ref_dt + dt.timedelta(days=start)).date()
        end_date = (self._cal.ref_dt + dt.timedelta(days=end)).date()

        return in_half_open_date(start_date, target_date, end_date)


class WeekNamespace(UnitNamespace):
    """Week-specific namespace that implements _in_impl with week logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Week-specific logic (moved from cal.in_weeks)."""
        from ._util import in_half_open_date
        from ._cal import normalize_weekday

        week_start_day = normalize_weekday("monday")  # default week start

        target_date = self._cal.target_dt.date()
        base_date = self._cal.ref_dt.date()

        # Calculate the start of the current week based on week_start_day
        days_since_week_start = (base_date.weekday() - week_start_day) % 7
        current_week_start = base_date - dt.timedelta(days=days_since_week_start)

        # Calculate week boundaries
        start_week_start = current_week_start + dt.timedelta(weeks=start)
        end_week_start = current_week_start + dt.timedelta(weeks=end)
        # Half-open semantics for weeks: `end_week_start` is already the
        # exclusive start-of-week produced by the normalized `end` value;
        # do not add an extra week here.
        end_week_exclusive = end_week_start

        return in_half_open_date(start_week_start, target_date, end_week_exclusive)


class MonthNamespace(UnitNamespace):
    """Month-specific namespace that implements _in_impl with month logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Month-specific logic (moved from cal.in_months)."""
        from ._util import in_half_open

        target_idx: int = self._month_index(self._cal.target_dt)
        start_idx = self._month_index(self._cal.ref_dt) + start
        end_idx = self._month_index(self._cal.ref_dt) + end

        # Half-open semantics for months: `end_idx` is the exclusive month
        # index (decorator normalization ensures single-arg calls behave as
        # a single unit window). Compare numeric month indices directly.
        return in_half_open(start_idx, target_idx, end_idx)

    def _month_index(self, d: dt.datetime) -> int:
        """Get a monotonic month index for comparison."""
        return d.year * 12 + d.month


class QuarterNamespace(UnitNamespace):
    """Quarter-specific namespace that implements _in_impl with quarter logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Quarter-specific logic (moved from cal.in_quarters)."""
        from ._util import in_half_open

        target_time = self._cal.target_dt
        base_time = self._cal.ref_dt

        # Use a monotonic quarter index (year * 4 + (quarter-1)) so we can
        # compare quarters with integer arithmetic (consistent with
        # `_month_index`). This avoids tuple allocations and is slightly
        # simpler to reason about.
        base_quarter = ((base_time.month - 1) // 3)  # 0..3 offset within year
        base_year = base_time.year

        def quarter_index_for_offset(offset: int) -> int:
            # Monotonic index where Q1 of year Y -> Y*4 + 0
            return base_year * 4 + base_quarter + offset

        start_idx = quarter_index_for_offset(start)
        end_idx = quarter_index_for_offset(end)

        # Target's monotonic quarter index
        target_quarter = ((target_time.month - 1) // 3)
        target_year = target_time.year
        target_idx = target_year * 4 + target_quarter

        # Check if target falls within the quarter range using half-open semantics
        return in_half_open(start_idx, target_idx, end_idx)


class YearNamespace(UnitNamespace):
    """Year-specific namespace that implements _in_impl with year logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Year-specific logic (moved from cal.in_years)."""
        from ._util import in_half_open

        target_year = self._cal.target_dt.year
        base_year = self._cal.ref_dt.year

        # Calculate year range boundaries
        start_year = base_year + start
        end_year = base_year + end

        # Use half-open semantics for years: `end_year` is exclusive. The
        # decorator already makes single-arg calls represent a single-year
        # half-open interval (start..start+1), so no extra shifting is
        # required here.
        return in_half_open(start_year, target_year, end_year)

    def _month_index(self, d):
        """Get a monotonic month index for comparison."""
        return d.year * 12 + d.month
