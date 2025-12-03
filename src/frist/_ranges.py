"""
Time unit namespaces for calendar and business logic operations.

This module provides the foundation for frist's time window filtering API through
namespace classes that encapsulate unit-specific logic. Each namespace inherits from
UnitNamespace and implements time range membership checks and utilities.

Cal namespaces (Minute, Hour, Day, Week, Month, Quarter, Year):
- Handle pure datetime calculations
- Use ref_dt and target_dt for range computations

Biz namespaces (BizDay, WorkingDay, FiscalQuarter, FiscalYear):
- Handle business-aware calculations
- Delegate to Biz object's policy-aware methods

Key features:
- Half-open interval semantics for range checks
- Inclusive "thru" sugar for end-inclusive ranges
- Month-specific utilities like nth_weekday calculations
"""

from __future__ import annotations

import datetime as dt
from typing import Protocol

from dateutil.rrule import FR, MO, MONTHLY, SA, SU, TH, TU, WE, rrule

from ._util import in_half_open_date


class CalProtocol(Protocol):
    """Protocol for objects that can create Cal-style namespaces."""

    @property
    def ref_dt(self) -> dt.datetime: ...
    @property
    def target_dt(self) -> dt.datetime: ...


class BizProtocol(Protocol):
    """Protocol for objects that can create Biz-style namespaces."""

    def in_business_days(self, start: int, end: int) -> bool: ...
    def in_working_days(self, start: int, end: int) -> bool: ...
    def in_fiscal_quarters(self, start: int, end: int) -> bool: ...
    def in_fiscal_years(self, start: int, end: int) -> bool: ...


__all__ = [
    "UnitNamespace",
    "MinuteNamespace",
    "HourNamespace",
    "DayNamespace",
    "WeekNamespace",
    "MonthNamespace",
    "QuarterNamespace",
    "YearNamespace",
    "BizDayNamespace",
    "WorkingDayNamespace",
    "FiscalQuarterNamespace",
    "FiscalYearNamespace",
]


class UnitNamespace:
    """Base namespace for time unit operations.

    Subclasses must implement `_in_impl(start: int, end: int) -> bool`.

    Usage examples:
      cal.month.in_(-2, 0)     # half-open (default)
      cal.month(-2, 0)         # maps to in_
      cal.month.thru(-2, 0)    # inclusive end
    """

    def __init__(self, cal: object) -> None:
        self._cal = cal

    def in_(self, start: int = 0, end: int | None = None) -> bool:
        """Half-open membership: start <= target < end.

        Single-arg (end omitted) -> single-unit window [start, start+1).
        """
        if end is None:
            end = start + 1
        if start >= end:
            raise ValueError(
                f"{self.__class__.__name__}.in_: {start=} must not be > than {end=}"
            )
        return self._in_impl(start, end)

    def _in_impl(self, start: int, end: int) -> bool:
        """Implemented by subclasses — contains the unit-specific logic."""
        raise NotImplementedError("implement _in_impl in subclass") # pragma: no cover

    @property
    def between(self):
        """Alias for in_ method."""
        return self.in_

    def __call__(self, start: int = 0, end: int | None = None) -> bool:
        return self.in_(start, end)

    def _thru_impl(self, start: int = 0, end: int | None = None) -> bool:
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
            def __call__(self, s: int = 0, e: int | None = None) -> bool:
                return parent._thru_impl(s, e)

        return _Thru()


class MinuteNamespace(UnitNamespace):
    """Minute-specific namespace that implements _in_impl with minute logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal) 

    def _in_impl(self, start: int, end: int) -> bool:
        """Minute-specific logic (moved from cal.in_minutes)."""
        from ._util import in_half_open_dt

        ref: dt.datetime = self._cal.ref_dt  # type: ignore
        target: dt.datetime = self._cal.target_dt  # type: ignore

        # compute minute-aligned boundaries
        start_time: dt.datetime = ref + dt.timedelta(minutes=start)
        start_minute: dt.datetime = start_time.replace(second=0, microsecond=0)

        end_time: dt.datetime = ref + dt.timedelta(minutes=end)
        end_minute: dt.datetime = end_time.replace(second=0, microsecond=0)

        return in_half_open_dt(start_minute, target, end_minute)


class HourNamespace(UnitNamespace):
    """Hour-specific namespace that implements _in_impl with hour logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Hour-specific logic (moved from cal.in_hours)."""
        from ._util import in_half_open_dt

        ref: dt.datetime = self._cal.ref_dt  # type: ignore
        target: dt.datetime = self._cal.target_dt  # type: ignore

        # compute hour-aligned boundaries
        start_time: dt.datetime = ref + dt.timedelta(hours=start)
        start_hour: dt.datetime = start_time.replace(minute=0, second=0, microsecond=0)

        end_time: dt.datetime = ref + dt.timedelta(hours=end)
        end_hour: dt.datetime = end_time.replace(minute=0, second=0, microsecond=0)

        return in_half_open_dt(start_hour, target, end_hour)


class DayNamespace(UnitNamespace):
    """Day-specific namespace that implements _in_impl with day logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Day-specific logic (moved from cal.in_days)."""

        target_date = self._cal.target_dt.date()  # type: ignore

        # Calculate the date range boundaries
        start_date = (self._cal.ref_dt + dt.timedelta(days=start)).date()  # type: ignore
        end_date = (self._cal.ref_dt + dt.timedelta(days=end)).date()  # type: ignore

        return in_half_open_date(start_date, target_date, end_date)


class WeekNamespace(UnitNamespace):
    """Week-specific namespace that implements _in_impl with week logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Week-specific logic (moved from cal.in_weeks)."""
        from ._cal import normalize_weekday
        from ._util import in_half_open_date

        week_start_day = normalize_weekday("monday")  # default week start

        target_date = self._cal.target_dt.date()  # type: ignore
        base_date = self._cal.ref_dt.date()  # type: ignore

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

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Month-specific logic (moved from cal.in_months)."""
        from ._util import in_half_open

        target_idx: int = self._month_index(self._cal.target_dt)  # type: ignore
        start_idx = self._month_index(self._cal.ref_dt) + start  # type: ignore
        end_idx = self._month_index(self._cal.ref_dt) + end  # type: ignore

        # Half-open semantics for months: `end_idx` is the exclusive month
        # index (decorator normalization ensures single-arg calls behave as
        # a single unit window). Compare numeric month indices directly.
        return in_half_open(start_idx, target_idx, end_idx)

    def _month_index(self, d: dt.datetime) -> int:
        """Get a monotonic month index for comparison."""
        return d.year * 12 + d.month

    def nth_weekday(self, weekday: str, n: int) -> dt.datetime:
        """
        Get the datetime of the nth occurrence of weekday in ref_dt's month.

        Uses dateutil.rrule for reliable, tested date calculations.

        Args:
            weekday: "monday", "tuesday", etc.
            n: 1=first, 2=second, -1=last, -2=second-to-last, etc.

        Returns:
            The datetime of the nth occurrence (at midnight)

        Raises:
            ValueError: If the nth occurrence doesn't exist
        """
        from ._cal import normalize_weekday

        ref_date:dt.date = self._cal.ref_dt.date()  # type: ignore
        weekday_num = normalize_weekday(weekday)

        # Map weekday number to rrule weekday
        weekday_map = {0: MO, 1: TU, 2: WE, 3: TH, 4: FR, 5: SA, 6: SU}
        rrule_weekday = weekday_map[weekday_num]

        # Create rrule for nth occurrence in the month
        month_start:dt.datetime = dt.datetime(ref_date.year, ref_date.month, 1)
        month_end:dt.datetime = dt.datetime(ref_date.year, ref_date.month + 1, 1) - dt.timedelta(
            days=1
        )

        # Use rrule to find the nth occurrence
        rule = rrule(
            MONTHLY,
            byweekday=rrule_weekday(n),  # n can be negative for "last"
            dtstart=month_start,
            until=month_end,
            count=1,
        )

        try:
            occurrence = list(rule)[0]
            return occurrence.replace(hour=0, minute=0, second=0, microsecond=0)
        except IndexError:
            raise ValueError(
                f"No {n}th {weekday} in {ref_date.year}-{ref_date.month:02d}"
            )

    def is_nth_weekday(self, weekday: str, n: int) -> bool:
        """
        Check if target_dt is the nth occurrence of weekday in its month.
        """
        try:
            nth_datetime = self.nth_weekday(weekday, n)
            return self._cal.target_dt.date() == nth_datetime.date()  # type: ignore
        except ValueError:
            return False


class QuarterNamespace(UnitNamespace):
    """Quarter-specific namespace that implements _in_impl with quarter logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Quarter-specific logic (moved from cal.in_quarters)."""
        from ._util import in_half_open

        target_time = self._cal.target_dt  # type: ignore
        base_time = self._cal.ref_dt  # type: ignore

        # Use a monotonic quarter index (year * 4 + (quarter-1)) so we can
        # compare quarters with integer arithmetic (consistent with
        # `_month_index`). This avoids tuple allocations and is slightly
        # simpler to reason about.
        base_quarter = (base_time.month - 1) // 3  # 0..3 offset within year
        base_year = base_time.year

        def quarter_index_for_offset(offset: int) -> int:
            # Monotonic index where Q1 of year Y -> Y*4 + 0
            return base_year * 4 + base_quarter + offset

        start_idx = quarter_index_for_offset(start)
        end_idx = quarter_index_for_offset(end)

        # Target's monotonic quarter index
        target_quarter = (target_time.month - 1) // 3
        target_year = target_time.year
        target_idx = target_year * 4 + target_quarter

        # Check if target falls within the quarter range using half-open semantics
        return in_half_open(start_idx, target_idx, end_idx)


class YearNamespace(UnitNamespace):
    """Year-specific namespace that implements _in_impl with year logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)  # no fn needed

    def _in_impl(self, start: int, end: int) -> bool:
        """Year-specific logic (moved from cal.in_years)."""
        from ._util import in_half_open

        target_year:int = self._cal.target_dt.year  # type: ignore
        base_year:int = self._cal.ref_dt.year  # type: ignore

        # Calculate year range boundaries
        start_year:int = base_year + start
        end_year:int = base_year + end

        # Use half-open semantics for years: `end_year` is exclusive. The
        # decorator already makes single-arg calls represent a single-year
        # half-open interval (start..start+1), so no extra shifting is
        # required here.
        return in_half_open(start_year, target_year, end_year)

    def day_of_year(self) -> int:
        """
        Returns the day of the year for target_dt (1-based, Jan 1 = 1).
        """
        return self._cal.target_dt.timetuple().tm_yday  # type: ignore

    def is_day_of_year(self, n: int) -> bool:
        """
        Returns True if target_dt is the nth day of its year (1-based).
        """
        return self.day_of_year() == n
    
class BizDayNamespace(UnitNamespace):
    """Business day-specific namespace that implements _in_impl with business day logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        """Business day-specific logic (moved from biz.in_business_days)."""
        return self._cal.in_business_days(start, end)  # type: ignore


class WorkingDayNamespace(UnitNamespace):
    """Working day-specific namespace that implements _in_impl with working day logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        """Working day-specific logic (moved from biz.in_working_days)."""
        return self._cal.in_working_days(start, end)  # type: ignore


class FiscalQuarterNamespace(UnitNamespace):
    """Fiscal quarter-specific namespace that implements _in_impl with fiscal quarter logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        """Fiscal quarter-specific logic (moved from biz.in_fiscal_quarters)."""
        return self._cal.in_fiscal_quarters(start, end)  # type: ignore


class FiscalYearNamespace(UnitNamespace):
    """Fiscal year-specific namespace that implements _in_impl with fiscal year logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        """Fiscal year-specific logic (moved from biz.in_fiscal_years)."""
        return self._cal.in_fiscal_years(start, end)  # type: ignore
