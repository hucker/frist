"""
Fiscal quarter unit adapter for `Biz`.

Implements `.in_(offset)` for fiscal quarters derived from policy start month
using the provided policy.
"""
from __future__ import annotations

from .._util import in_half_open
from .._biz_policy import BizPolicy
from ._base import CalProtocol, UnitName

def _fiscal_year(dt_, fy_start_month: int) -> int:
    return dt_.year if dt_.month >= fy_start_month else dt_.year - 1


def _fiscal_quarter(dt_, fy_start_month: int) -> int:
    if dt_.month >= fy_start_month:
        offset = (dt_.month - fy_start_month) % 12
    else:
        offset = (dt_.month + 12 - fy_start_month) % 12
    return (offset // 3) + 1


class FiscalQuarterUnit(UnitName[CalProtocol]):
    """Fiscal quarter-specific unit computed from Biz policy start month."""

    def __init__(self, cal: CalProtocol, policy: BizPolicy) -> None:
        super().__init__(cal)
        self._policy = policy

    def _in_impl(self, start: int, end: int) -> bool:
        fy_start_month = self._policy.fiscal_year_start_month
        base_fy = _fiscal_year(self._cal.ref_dt, fy_start_month)
        base_fq = _fiscal_quarter(self._cal.ref_dt, fy_start_month)
        base_idx = base_fy * 4 + (base_fq - 1)

        start_idx = base_idx + start
        end_idx = base_idx + end

        target_fy = _fiscal_year(self._cal.target_dt, fy_start_month)
        target_fq = _fiscal_quarter(self._cal.target_dt, fy_start_month)
        target_idx = target_fy * 4 + (target_fq - 1)

        return in_half_open(start_idx, target_idx, end_idx)

    @property
    def val(self) -> int:
        fy_start_month = self._policy.fiscal_year_start_month
        return _fiscal_quarter(self._cal.target_dt, fy_start_month)

    @property
    def name(self) -> str:
        return f"Q{self.val}"
