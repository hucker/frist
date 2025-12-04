from __future__ import annotations

import datetime as dt

from ._base import UnitNamespace, CalProtocol
from .._util import in_half_open


class YearNamespace(UnitNamespace[CalProtocol]):
    """Year-specific namespace implementing year half-open logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:

        target_year: int = self._cal.target_dt.year
        base_year: int = self._cal.ref_dt.year

        start_year: int = base_year + start
        end_year: int = base_year + end

        return in_half_open(start_year, target_year, end_year)

    def day_of_year(self) -> int:
        return self._cal.target_dt.timetuple().tm_yday

    def is_day_of_year(self, n: int) -> bool:
        return self.day_of_year() == n

    @property
    def val(self) -> int:
        return self._cal.target_dt.year

    @property
    def day(self) -> int:
        return self._cal.target_dt.timetuple().tm_yday
