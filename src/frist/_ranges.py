"""
Compatibility shim for legacy imports.

This module re-exports unit namespace classes from `frist.units` to avoid
breaking existing import paths while the codebase was refactored to per-file
modules under `src/frist/units/`.
"""

from .units import (
    UnitNamespace,
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
