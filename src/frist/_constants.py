
"""
Constants used throughout the Frist package.
"""

from typing import Dict, Final

# Time conversion constants
SECONDS_PER_MINUTE: Final[int] = 60
SECONDS_PER_HOUR: Final[int] = 3600
SECONDS_PER_DAY: Final[int] = 86400
SECONDS_PER_WEEK: Final[int] = 604800  # 7 * 24 * 60 * 60

# Advanced time constants for age calculations
DAYS_PER_MONTH: Final[float] = 30.44  # Average days per month
DAYS_PER_YEAR: Final[float] = 365.25  # Average days per year (accounting for leap years)
SECONDS_PER_MONTH: Final[int] = int(DAYS_PER_MONTH * SECONDS_PER_DAY)  # 2630016
SECONDS_PER_YEAR: Final[int] = int(DAYS_PER_YEAR * SECONDS_PER_DAY)  # 31557600

# Default fallback timestamp (1 day after Unix epoch to avoid timezone issues)
DEFAULT_FALLBACK_TIMESTAMP: Final[int] = SECONDS_PER_DAY

# Calendar constants
DAYS_PER_WEEK: Final[int] = 7
MONTHS_PER_YEAR: Final[int] = 12

# Unified weekday mapping: all supported names/abbreviations to weekday index
WEEKDAY_INDEX: Final[Dict[str, int]] = {
    "monday": 0, "mon": 0, "mo": 0,
    "tuesday": 1, "tue": 1, "tu": 1,
    "wednesday": 2, "wed": 2, "we": 2,
    "thursday": 3, "thu": 3, "th": 3,
    "friday": 4, "fri": 4, "fr": 4,
    "saturday": 5, "sat": 5, "sa": 5,
    "sunday": 6, "sun": 6, "su": 6,
}
__all__ = [
    "SECONDS_PER_MINUTE",
    "SECONDS_PER_HOUR",
    "SECONDS_PER_DAY",
    "SECONDS_PER_WEEK",
    "DAYS_PER_MONTH",
    "DAYS_PER_YEAR",
    "SECONDS_PER_MONTH",
    "SECONDS_PER_YEAR",
    "DEFAULT_FALLBACK_TIMESTAMP",
    "DAYS_PER_WEEK",
    "MONTHS_PER_YEAR",
    "WEEKDAY_INDEX",
]
