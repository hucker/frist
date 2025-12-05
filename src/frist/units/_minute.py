"""
Minute namespace adapter for `Cal`.

Provides `.in_(offset)` and related helpers to test minute-aligned half-open
windows relative to a reference datetime. Delegates to `Cal` implementation.
"""
from __future__ import annotations

import datetime as dt

from ._base import UnitNamespace, CalProtocol
from .._util import in_half_open_dt


class MinuteNamespace(UnitNamespace[CalProtocol]):
    """Minute-specific namespace implementing minute-aligned half-open logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:

        ref: dt.datetime = self._cal.ref_dt
        target: dt.datetime = self._cal.target_dt

        start_time: dt.datetime = ref + dt.timedelta(minutes=start)
        start_minute: dt.datetime = start_time.replace(second=0, microsecond=0)

        end_time: dt.datetime = ref + dt.timedelta(minutes=end)
        end_minute: dt.datetime = end_time.replace(second=0, microsecond=0)

        return in_half_open_dt(start_minute, target, end_minute)

    @property
    def val(self) -> int:
        return self._cal.target_dt.minute
