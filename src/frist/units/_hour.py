"""
Hour namespace adapter for `Cal`.

Provides `.in_(offset)` and helpers for hour-aligned half-open windows relative
to the reference datetime. Delegates to `Cal` implementation.
"""
from __future__ import annotations

import datetime as dt

from ._base import UnitNamespace, CalProtocol
from .._util import in_half_open_dt


class HourNamespace(UnitNamespace[CalProtocol]):
    """Hour-specific namespace implementing hour-aligned half-open logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:

        ref: dt.datetime = self._cal.ref_dt
        target: dt.datetime = self._cal.target_dt

        start_time: dt.datetime = ref + dt.timedelta(hours=start)
        start_hour: dt.datetime = start_time.replace(minute=0, second=0, microsecond=0)

        end_time: dt.datetime = ref + dt.timedelta(hours=end)
        end_hour: dt.datetime = end_time.replace(minute=0, second=0, microsecond=0)

        return in_half_open_dt(start_hour, target, end_hour)

    @property
    def val(self) -> int:
        return self._cal.target_dt.hour
