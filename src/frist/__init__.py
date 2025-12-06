"""
frist: Standalone datetime utility package

Provides robust tools for:
    - Age and duration calculations across multiple time units
    - Calendar window filtering (days, weeks, months, quarters, years)
    - Fiscal year/quarter logic and holiday detection
    - Flexible datetime parsing and normalization

Designed for use in any Python project requiring advanced datetime analysis, 
not limited to file operations.

Exports:
    Chrono   -- Main datetime utility class
    Age       -- Duration and age calculations
    Cal       -- Calendar window and filtering logic
    Biz       -- Business logic including fiscal year/quarter and holidays
    BizPolicy -- Configurable calendar policies (fiscal year start, holidays)
"""
from ._age import Age
from ._biz import Biz
from ._biz_policy import BizPolicy
from ._cal import Cal
from ._frist import Chrono
from .units import (
    BizDayUnit,
    DayUnit,
    FiscalQuarterUnit,
    FiscalYearUnit,
    HourUnit,
    MinuteUnit,
    MonthUnit,
    QuarterUnit,
    UnitName,
    SecondUnit,
    WeekUnit,
    WorkingDayUnit,
    YearUnit,
)

__version__ = "0.17.0"
__author__ = "Chuck Bass"

__all__ = [
    "Chrono",
    "Age",
    "Cal",
    "Biz",
    "BizPolicy",
    # Units re-exported at top-level for convenience
    "UnitName",
        "SecondUnit",
    "MinuteUnit",
    "HourUnit",
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
