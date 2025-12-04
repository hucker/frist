"""
Namespace units package.

This module re-exports unit namespace classes to provide a stable import surface
(e.g., `from frist.units import DayNamespace`). The implementation will be
incrementally migrated from `_ranges.py` into per-file modules like `_day.py`,
`_week.py`, etc., without changing the public API.
"""

# Temporary re-exports from the existing monolithic module.
# As we migrate, these imports will point to per-file modules.
from ._base import UnitNamespace
from ._biz_day import BizDayNamespace
from ._day import DayNamespace
from ._fiscal_quarter import FiscalQuarterNamespace
from ._fiscal_year import FiscalYearNamespace
from ._hour import HourNamespace
from ._minute import MinuteNamespace
from ._month import MonthNamespace
from ._quarter import QuarterNamespace
from ._week import WeekNamespace
from ._work_day import WorkingDayNamespace
from ._year import YearNamespace

__all__ = [
    "UnitNamespace",
    "MinuteNamespace",
    "HourNamespace",
    "DayNamespace",
    "WeekNamespace",
    "MonthNamespace",
    "QuarterNamespace",
    "YearNamespace",
    "BizDayNamespace",
    "WorkingDayNamespace",
    "FiscalQuarterNamespace",
    "FiscalYearNamespace",
]
