"""
Frist: Standalone datetime utility package

Provides robust tools for:
    - Age and duration calculations across multiple time units
    - Calendar window filtering (days, weeks, months, quarters, years)
    - Fiscal year/quarter logic and holiday detection
    - Flexible datetime parsing and normalization

Designed for use in any Python project requiring advanced datetime analysis, not limited to file operations.

Exports:
    Frist   -- Main datetime utility class
    Age       -- Duration and age calculations
    Cal       -- Calendar window and filtering logic
    TimeSpan  -- Time span representation for advanced calculations
"""

from ._age import Age
from ._cal import Cal, TimeSpan
from ._frist import Frist

__version__ = "0.8.0"
__author__ = "Chuck Bass"

__all__ = ["Frist", "Age", "Cal", "TimeSpan"]
