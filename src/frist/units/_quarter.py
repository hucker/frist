"""
Quarter namespace adapter for `Cal`.

Supports calendar quarter half-open windows (Q1–Q4) via `.in_(offset)` while
delegating core logic to `Cal`.
"""
from __future__ import annotations

import datetime as dt

from ._base import UnitNamespace, CalProtocol
from .._util import in_half_open


class QuarterNamespace(UnitNamespace[CalProtocol]):
    """Quarter-specific namespace implementing quarter-index half-open logic."""

    def __init__(self, cal: CalProtocol) -> None:
        super().__init__(cal)

    def _in_impl(self, start: int, end: int) -> bool:

        target_time = self._cal.target_dt
        base_time = self._cal.ref_dt

        base_quarter = (base_time.month - 1) // 3  # 0..3
        base_year = base_time.year

        def quarter_index_for_offset(offset: int) -> int:
            return base_year * 4 + base_quarter + offset

        start_idx = quarter_index_for_offset(start)
        end_idx = quarter_index_for_offset(end)

        target_quarter = (target_time.month - 1) // 3
        target_year = target_time.year
        target_idx = target_year * 4 + target_quarter

        return in_half_open(start_idx, target_idx, end_idx)

    @property
    def val(self) -> int:
        target_time: dt.datetime = self._cal.target_dt
        return ((target_time.month - 1) // 3) + 1

    @property
    def name(self) -> str:
        return f"Q{self.val}"
