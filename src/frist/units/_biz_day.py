from __future__ import annotations

from ._base import UnitNamespace, BizProtocol


class BizDayNamespace(UnitNamespace[BizProtocol]):
    """Business day-specific namespace delegating to Biz policy logic."""

    def __init__(self, cal: BizProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:
        return self._cal.in_business_days(start, end)
