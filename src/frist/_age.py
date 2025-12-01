"""
Age property implementation for frist package.

Handles age calculations in various time units, supporting both file-based and standalone usage.
"""

import datetime as dt

import re

from ._constants import (
    DAYS_PER_WEEK,
    DAYS_PER_MONTH,
    DAYS_PER_YEAR,
    SECONDS_PER_DAY,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    SECONDS_PER_MONTH,
    SECONDS_PER_WEEK,
    SECONDS_PER_YEAR,
)
from ._types import TimeLike, time_pair, to_datetime


class Age:
    """
    Property class for handling age calculations in various time units.

    Features:
        - Computes age and duration between two datetimes, timestamps, or numeric values.
        - Supports flexible initialization: accepts dt.datetime, dt.date, float, or int for start and end times.
        - Uses a configurable BizPolicy for business calendar logic (workdays, holidays, business hours).
        - Provides properties for age in seconds, minutes, hours, days, weeks, months, years, and fractional working days.
        - Allows updating start and end times via the `set_times` method (kwargs-only, preserves previous values if None).

    Initialization:
        Age(start_time, end_time=None, formats=None)
        - start_time: TimeLike (dt.datetime, dt.date, float, int, or str) (required)
        - end_time: TimeLike or None (defaults to now)
        - formats: list[str] or None (custom datetime formats for string parsing)

    Updating times:
        age.set_times(start_time=..., end_time=...)
        - Both arguments are optional and kwargs-only.
        - If a value is None, the previous value is retained.
        - Supports dt.datetime, dt.date, float, or int for each argument.

    Example:
        age = Age(dt.datetime(2020, 1, 1))
        age.set_times(end_time=dt.datetime(2024, 1, 1))
        print(age.years)  # 4.0

    Note:
        - All calculations use full datetimes (date and time); dates are converted to datetimes at midnight.
        - Timezones are not supported.
        - The class is designed for correctness and flexibility, supporting arbitrary calendar policies and update patterns.
    """

    def __init__(
        self,
        start_time: TimeLike,
        end_time: TimeLike | None = None,
        formats: list[str] | None = None,
    ):
        self._start_time: dt.datetime
        self._end_time: dt.datetime
        self._start_time, self._end_time = time_pair(start_time=start_time, end_time=end_time, formats__=formats)


    @staticmethod
    def _next_month_year(year: int, month: int) -> tuple[int, int]:
        """Return (next_year, next_month) for month rollover."""
        if month == 12:
            return year + 1, 1
        return year, month + 1

    @property
    def start_time(self) -> dt.datetime:
        return self._start_time

    @property
    def end_time(self) -> dt.datetime:
        return self._end_time

    def set_times(
        self,
        *,
        start_time: TimeLike | None = None,
        end_time: TimeLike | None = None,
        formats: list[str] | None = None,
    ) -> None:
        """
        WARNING: This method mutates the Age instance in place, beware of side effects during threaded operation.


        Update the start and/or end time for this Age instance.

        This method is kwargs-only: you must specify start_time and/or end_time as keyword arguments.
        If a value is None, the previous value is retained.

        Parameters:
            start_time (TimeLike | None): New start time. If None, keeps previous value.
            end_time (TimeLike | None): New end time. If None, keeps previous value.
            formats (list[str] | None): Custom datetime formats for string parsing.

        Type support:
            - dt.datetime: Used directly (timezones not supported)
            - dt.date: Converted to datetime at midnight
            - float/int: Interpreted as a POSIX timestamp
            - str: Parsed using supported datetime formats

        Raises:
            TypeError: If a provided value is not a supported type
            ValueError: If start_time is not set at least once

        Example:
            age.set_times(start_time=dt.datetime(2020, 1, 1))
            age.set_times(end_time=dt.datetime(2024, 1, 1))
            age.set_times(start_time=1700000000.0)  # POSIX timestamp
            age.set_times(start_time="2023-12-25 14:30:00")  # String format
        """
        if start_time is not None:
            self._start_time = to_datetime(start_time, formats)

        if end_time is not None:
            self._end_time = to_datetime(end_time, formats)

    # Suggestion: You can use set_times inside __init__ to centralize type handling and validation for start/end times. This makes future updates easier and keeps logic DRY.


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
        return self.days / DAYS_PER_WEEK

    @property
    def months(self) -> float:
        """Get age in months (approximate - 30.44 days)."""
        return self.days / DAYS_PER_MONTH
    
    @property
    def months_precise(self) -> float:
        """
        Get age in months (precise calculation based on calendar months).
        Partial months at start and end are calculated using the actual number of seconds in those months (including time portion).
        Full months in between are simply counted as 1.0 each.
        """
        start = self.start_time
        end = self.end_time
        if start > end:
            raise ValueError("start_time must be before end_time")
        if start >= end:
            return 0.0
        # If start and end are in the same month
        if start.year == end.year and start.month == end.month:
            month_start = dt.datetime(start.year, start.month, 1)
            next_year, next_month = self._next_month_year(start.year, start.month)
            month_end = dt.datetime(next_year, next_month, 1)
            total_seconds = (month_end - month_start).total_seconds()
            interval_seconds = (end - start).total_seconds()
            return interval_seconds / total_seconds
        # First month fraction
        next_year, next_month = self._next_month_year(start.year, start.month)
        start_month_end = dt.datetime(next_year, next_month, 1)
        first_month_seconds = (start_month_end - start).total_seconds()
        total_start_month_seconds = (start_month_end - dt.datetime(start.year, start.month, 1)).total_seconds()
        first_month_fraction = first_month_seconds / total_start_month_seconds
        # Last month fraction
        last_month_start = dt.datetime(end.year, end.month, 1)
        next_year, next_month = self._next_month_year(end.year, end.month)
        last_month_end = dt.datetime(next_year, next_month, 1)
        last_month_seconds = (end - last_month_start).total_seconds()
        total_last_month_seconds = (last_month_end - last_month_start).total_seconds()
        last_month_fraction = last_month_seconds / total_last_month_seconds if last_month_seconds > 0 else 0.0
        # Count full months in between
        # Move start to first of next month
        full_months = 0
        current_year, current_month = self._next_month_year(start.year, start.month)
        while (current_year, current_month) != (end.year, end.month):
            full_months += 1
            current_year, current_month = self._next_month_year(current_year, current_month)
        return first_month_fraction + full_months + last_month_fraction

    @property
    def years(self) -> float:
        """
        Get age in years (approximate - 365.25 days, can be negative).

        Note:
            This calculation uses 365.25 days per year for approximation, which averages leap and non-leap years.
        """
        # Allow negative ages if base_time is before timestamp
        # Uses 365.25 days/year for approximation; does not distinguish leap/non-leap years.
        return self.days / DAYS_PER_YEAR
    
    @property
    def years_precise(self) -> float:
        """
        Get age in years (precise calculation based on calendar years).
        Fractional years are calculated using the actual number of days in each year.
        """
        scale = 1.0
        start:dt.datetime = self.start_time
        end:dt.datetime = self.end_time
        if start > end:
            start, end = end, start
            scale = -1.0
        
        def _fractional_days(dt1: dt.datetime, dt2: dt.datetime) -> float:
            """Calculate fractional days between two datetimes."""
            return (dt2 - dt1).total_seconds() / (24 * 3600)
        
        # Same year: fraction only
        if start.year == end.year:
            days_in_year = (dt.datetime(start.year + 1, 1, 1) - dt.datetime(start.year, 1, 1)).days
            return scale * (_fractional_days(start, end) / days_in_year)
        
        # First year fraction
        end_of_first_year = dt.datetime(start.year, 12, 31, 23, 59, 59)
        days_in_first_year = (dt.datetime(start.year + 1, 1, 1) - dt.datetime(start.year, 1, 1)).days
        first_year_fraction = _fractional_days(start, end_of_first_year) / days_in_first_year
        
        # Last year fraction
        start_of_last_year = dt.datetime(end.year, 1, 1)
        days_in_last_year = (dt.datetime(end.year + 1, 1, 1) - dt.datetime(end.year, 1, 1)).days
        last_year_fraction = _fractional_days(start_of_last_year, end) / days_in_last_year
        
        # Full years in between
        full_years = end.year - start.year - 1
        
        return scale * (first_year_fraction + full_years + last_year_fraction)


    @staticmethod
    def parse(age_str: str) -> float:
        """
        Parse an age string and return the age in seconds.

        Examples:
            "30" -> 30 seconds
            "5m" -> 300 seconds (5 minutes)
            "2 h" -> 7200 seconds (2 hours)
            "3d" -> 259200 seconds (3 days)
            "1w" -> 604800 seconds (1 week)
            "2months" -> 5260032 seconds (2 months)
            "1 y" -> 31557600 seconds (1 year)
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

#a1 = Age(dt.datetime(2020,1,1), dt.datetime(2021,1,1))
#print(a1.years_precise)