from __future__ import annotations
from typing import Callable, Optional

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

    def in_(self, start: int = 0, end: Optional[int] = None) -> bool:
        """Override to use _in_impl instead of _fn."""
        if end is None:
            end = start + 1
        if start >= end:
            raise ValueError(f"in_: start ({start}) must not be greater than end ({end})")
        return self._in_impl(start, end)

    def _in_impl(self, start: int, end: int) -> bool:
        """Minute-specific logic (moved from cal.in_minutes)."""
        import datetime as _dt
        from ._util import in_half_open_dt

        ref = self._cal.ref_dt
        target = self._cal.target_dt

        # compute minute-aligned boundaries
        start_time = ref + _dt.timedelta(minutes=start)
        start_minute = start_time.replace(second=0, microsecond=0)

        end_time = ref + _dt.timedelta(minutes=end)
        end_minute = end_time.replace(second=0, microsecond=0)

        return in_half_open_dt(start_minute, target, end_minute)


class HourNamespace(UnitNamespace):
    """Hour-specific namespace that implements _in_impl with hour logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def in_(self, start: int = 0, end: Optional[int] = None) -> bool:
        """Override to use _in_impl instead of _fn."""
        if end is None:
            end = start + 1
        if start >= end:
            raise ValueError(f"in_: start ({start}) must not be greater than end ({end})")
        return self._in_impl(start, end)

    def _in_impl(self, start: int, end: int) -> bool:
        """Hour-specific logic (moved from cal.in_hours)."""
        import datetime as _dt
        from ._util import in_half_open_dt

        ref = self._cal.ref_dt
        target = self._cal.target_dt

        # compute hour-aligned boundaries
        start_time = ref + _dt.timedelta(hours=start)
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)

        end_time = ref + _dt.timedelta(hours=end)
        end_hour = end_time.replace(minute=0, second=0, microsecond=0)

        return in_half_open_dt(start_hour, target, end_hour)


class DayNamespace(UnitNamespace):
    """Day-specific namespace that implements _in_impl with day logic."""

    def __init__(self, cal: object) -> None:
        super().__init__(cal)  # no fn needed

    def in_(self, start: int = 0, end: Optional[int] = None) -> bool:
        """Override to use _in_impl instead of _fn."""
        if end is None:
            end = start + 1
        if start >= end:
            raise ValueError(f"in_: start ({start}) must not be greater than end ({end})")
        return self._in_impl(start, end)

    def _in_impl(self, start: int, end: int) -> bool:
        """Day-specific logic (moved from cal.in_days)."""
        import datetime as _dt
        from ._util import in_half_open_date

        target_date = self._cal.target_dt.date()

        # Calculate the date range boundaries
        start_date = (self._cal.ref_dt + _dt.timedelta(days=start)).date()
        end_date = (self._cal.ref_dt + _dt.timedelta(days=end)).date()

        return in_half_open_date(start_date, target_date, end_date)
