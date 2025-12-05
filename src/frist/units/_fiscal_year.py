"""
Fiscal year unit adapter for `Biz`.

Provides `.in_(offset)` checks for fiscal years computed from policy start
month, delegating to `Biz`.
"""
from __future__ import annotations

from ._base import BizProtocol, UnitName


class FiscalYearUnit(UnitName[BizProtocol]):
    """Fiscal year-specific unit delegating to Biz policy logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        return self._cal.in_fiscal_years(start, end)

    @property
    def val(self) -> int:
        return self._cal.fiscal_year
