from __future__ import annotations

from ._base import UnitNamespace, BizProtocol


class FiscalQuarterNamespace(UnitNamespace[BizProtocol]):
    """Fiscal quarter-specific namespace delegating to Biz policy logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        return self._cal.in_fiscal_quarters(start, end)

    @property
    def val(self) -> int:
        return self._cal.fiscal_quarter

    @property
    def name(self) -> str:
        return f"Q{self.val}"
