"""
Second unit adapter for `Cal`.

Provides `.in_(offset)` to test second-aligned half-open windows relative to
the reference datetime.
"""
from __future__ import annotations

import datetime as dt

from .._util import in_half_open_dt
from ._base import CalProtocol, UnitName


class SecondUnit(UnitName[CalProtocol]):
    """Second-specific unit implementing second-aligned half-open logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        ref: dt.datetime = self._cal.ref_dt
        target: dt.datetime = self._cal.target_dt

        start_time: dt.datetime = ref + dt.timedelta(seconds=start)
        start_second: dt.datetime = start_time.replace(microsecond=0)

        end_time: dt.datetime = ref + dt.timedelta(seconds=end)
        end_second: dt.datetime = end_time.replace(microsecond=0)

        return in_half_open_dt(start_second, target, end_second)

    @property
    def val(self) -> int:
        return self._cal.target_dt.second
