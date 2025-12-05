"""
Compatibility shim for legacy imports.

Re-exports unit namespaces from `frist.units`. Prefer importing from
`frist.units` directly in new code. This module may be removed in a future
major release.
"""

from .units import (
    MinuteUnit,
    HourNamespace,
    DayUnit,
    WeekUnit,
    MonthUnit,
    QuarterUnit,
    YearUnit,
    BizDayUnit,
    WorkingDayUnit,
    FiscalQuarterUnit,
    FiscalYearUnit,
)

__all__ = [
    "MinuteUnit",
    "HourNamespace",
    "DayUnit",
    "WeekUnit",
    "MonthUnit",
    "QuarterUnit",
    "YearUnit",
    "BizDayUnit",
    "WorkingDayUnit",
    "FiscalQuarterUnit",
    "FiscalYearUnit",
]
