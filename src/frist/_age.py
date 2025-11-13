"""
Age property implementation for frist package.

Handles age calculations in various time units, supporting both file-based and standalone usage.
"""

import datetime as dt

import re

from ._constants import (
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    SECONDS_PER_DAY,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    SECONDS_PER_MONTH,
    SECONDS_PER_WEEK,
    SECONDS_PER_YEAR,
)

from ._cal_policy import CalendarPolicy

class Age:
    """Property class for handling age calculations in various time units."""

    def __init__(
        self,
        start_time: dt.datetime | float | int,
        end_time: dt.datetime | float | int | None = None,
        cal_policy: CalendarPolicy | None = None,
    ):
        if isinstance(start_time, (float, int)):
            self.start_time = dt.datetime.fromtimestamp(start_time)
        elif isinstance(start_time, dt.datetime): # type: ignore # Explicit type check for runtime safety
            self.start_time = start_time
        else:
            raise TypeError("start_time must be datetime, float, or int")

        if end_time is None:
            self.end_time = dt.datetime.now()
        elif isinstance(end_time, (float, int)):
            self.end_time = dt.datetime.fromtimestamp(end_time)
        elif isinstance(end_time, dt.datetime): # type: ignore # Explicit type check for runtime safety
            self.end_time = end_time
        else:
            raise TypeError("end_time must be datetime, float, int, or None")

        if cal_policy is None:
            self._cal_policy: CalendarPolicy = CalendarPolicy()
        else:
            self._cal_policy: CalendarPolicy = cal_policy

    @property
    def cal_policy(self) -> CalendarPolicy:
        """Return the calendar policy object used by this Age instance."""
        return self._cal_policy

    @property
    def seconds(self) -> float:
        """Get age in seconds."""
        return (self.end_time - self.start_time).total_seconds()

    @property
    def minutes(self) -> float:
        """Get age in minutes."""
        return self.seconds / SECONDS_PER_MINUTE

    @property
    def hours(self) -> float:
        """Get age in hours."""
        return self.seconds / SECONDS_PER_HOUR

    @property
    def days(self) -> float:
        """Get age in days."""
        return self.seconds / SECONDS_PER_DAY

    @property
    def weeks(self) -> float:
        """Get age in weeks."""
        return self.days / 7

    @property
    def months(self) -> float:
        """Get age in months (approximate - 30.44 days)."""
        return self.days / DAYS_PER_MONTH

    @property
    def years(self) -> float:
        """Get age in years (approximate - 365.25 days, can be negative)."""
        # Allow negative ages if base_time is before timestamp
        return self.days / DAYS_PER_YEAR

    @staticmethod
    def parse(age_str: str) -> float:
        """
        Parse an age string and return the age in seconds.

        Examples:
            "30" -> 30 seconds
            "5m" -> 300 seconds (5 minutes)
            "2h" -> 7200 seconds (2 hours)
            "3d" -> 259200 seconds (3 days)
            "1w" -> 604800 seconds (1 week)
            "2months" -> 5260032 seconds (2 months)
            "1y" -> 31557600 seconds (1 year)
        """
        age_str = age_str.strip().lower()
        # Handle plain numbers (seconds), including negatives
        if re.match(r"^-?\d+(?:\.\d+)?$", age_str):
            return float(age_str)

        # Regular expression to parse age with unit, including negatives
        match = re.match(r"^(-?\d+(?:\.\d+)?)\s*([a-zA-Z]+)$", age_str)
   
        if not match:
            raise ValueError(f"Invalid age format: {age_str}")

        value: float = float(match.group(1))
        unit: str = match.group(2).lower()

        # Define multipliers (convert to seconds)
        unit_multipliers = {
            "s": 1,
            "sec": 1,
            "second": 1,
            "seconds": 1,
            "m": SECONDS_PER_MINUTE,
            "min": SECONDS_PER_MINUTE,
            "minute": SECONDS_PER_MINUTE,
            "minutes": SECONDS_PER_MINUTE,
            "h": SECONDS_PER_HOUR,
            "hr": SECONDS_PER_HOUR,
            "hour": SECONDS_PER_HOUR,
            "hours": SECONDS_PER_HOUR,
            "d": SECONDS_PER_DAY,
            "day": SECONDS_PER_DAY,
            "days": SECONDS_PER_DAY,
            "w": SECONDS_PER_WEEK,
            "week": SECONDS_PER_WEEK,
            "weeks": SECONDS_PER_WEEK,
            "month": SECONDS_PER_MONTH,
            "months": SECONDS_PER_MONTH,
            "y": SECONDS_PER_YEAR,
            "year": SECONDS_PER_YEAR,
            "years": SECONDS_PER_YEAR,
        }

        if unit not in unit_multipliers:
            raise ValueError(f"Unknown unit: {unit}")

        return value * unit_multipliers[unit]



__all__ = ["Age"]
