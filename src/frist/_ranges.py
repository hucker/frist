"""
Compatibility shim for legacy imports.

Re-exports unit namespaces from `frist.units`. Prefer importing from
`frist.units` directly in new code. This module may be removed in a future
major release.
"""

from .units import (
    MinuteNamespace,
    HourNamespace,
    DayNamespace,
    WeekNamespace,
    MonthNamespace,
    QuarterNamespace,
    YearNamespace,
    BizDayNamespace,
    WorkingDayNamespace,
    FiscalQuarterNamespace,
    FiscalYearNamespace,
)

__all__ = [
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
