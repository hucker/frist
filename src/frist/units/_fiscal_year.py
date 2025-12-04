from __future__ import annotations

from ._base import UnitNamespace, BizProtocol


class FiscalYearNamespace(UnitNamespace[BizProtocol]):
    """Fiscal year-specific namespace delegating to Biz policy logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        return self._cal.in_fiscal_years(start, end)

    @property
    def val(self) -> int:
        return self._cal.fiscal_year
