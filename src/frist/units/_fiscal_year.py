"""
Fiscal year unit adapter for `Biz`.

Implements `.in_(offset)` checks for fiscal years computed from policy start
month using the provided policy.
"""
from __future__ import annotations

from .._util import in_half_open
from .._biz_policy import BizPolicy
from ._base import CalProtocol, UnitName

def _fiscal_year(dt_, fy_start_month: int) -> int:
    return dt_.year if dt_.month >= fy_start_month else dt_.year - 1


class FiscalYearUnit(UnitName[CalProtocol]):
    """Fiscal year-specific unit computed from Biz policy start month."""

    def __init__(self, cal: CalProtocol, policy: BizPolicy) -> None:
        super().__init__(cal)
        self._policy = policy

    def _in_impl(self, start: int, end: int) -> bool:
        fy_start_month = self._policy.fiscal_year_start_month
        base_fy = _fiscal_year(self._cal.ref_dt, fy_start_month)
        target_fy = _fiscal_year(self._cal.target_dt, fy_start_month)
        start_year = base_fy + start
        end_year = base_fy + end
        return in_half_open(start_year, target_fy, end_year)

    @property
    def val(self) -> int:
        fy_start_month = self._policy.fiscal_year_start_month
        return _fiscal_year(self._cal.target_dt, fy_start_month)
