"""
Working-day unit adapter for `Biz`.

Provides `.in_(offset)` for policy-defined workdays (ignores holidays) using
business hours to compute boundaries where needed. Delegates to `Biz`.
"""
from __future__ import annotations

from ._base import BizProtocol, UnitName


class WorkingDayUnit(UnitName[BizProtocol]):
    """Working day-specific unit delegating to Biz policy logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        return self._cal.in_working_days(start, end)
