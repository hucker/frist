"""
frist: Standalone datetime utility package

Provides robust tools for:
    - Age and duration calculations across multiple time units
    - Calendar window filtering (days, weeks, months, quarters, years)
    - Fiscal year/quarter logic and holiday detection
    - Flexible datetime parsing and normalization

Designed for use in any Python project requiring advanced datetime analysis, not limited to file operations.

Exports:
    Chrono   -- Main datetime utility class
    Age       -- Duration and age calculations
    Cal       -- Calendar window and filtering logic
    CalendarPolicy -- Configurable calendar policies (fiscal year start, holidays)
"""
from ._age import Age
from ._cal import Cal
from ._cal_policy import CalendarPolicy
from ._frist import Chrono

__version__ = "0.10.0"
__author__ = "Chuck Bass"

__all__ = ["Chrono", "Age",  "Cal" ,"CalendarPolicy" ]
