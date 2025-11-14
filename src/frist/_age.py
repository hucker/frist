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
    """
    Property class for handling age calculations in various time units.

    Features:
        - Computes age and duration between two datetimes, timestamps, or numeric values.
        - Supports flexible initialization: accepts dt.datetime, float, or int for start and end times.
        - Uses a configurable CalendarPolicy for business calendar logic (workdays, holidays, business hours).
        - Provides properties for age in seconds, minutes, hours, days, weeks, months, years, and fractional working days.
        - Allows updating start and end times via the `set_times` method (kwargs-only, preserves previous values if None).

    Initialization:
        Age(start_time, end_time=None, cal_policy=None)
        - start_time: dt.datetime, float, or int (required)
        - end_time: dt.datetime, float, int, or None (defaults to now)
        - cal_policy: CalendarPolicy (optional)

    Updating times:
        age.set_times(start_time=..., end_time=...)
        - Both arguments are optional and kwargs-only.
        - If a value is None, the previous value is retained.
        - Supports dt.datetime, float, or int for each argument.

    Example:
        age = Age(dt.datetime(2020, 1, 1))
        age.set_times(end_time=dt.datetime(2024, 1, 1))
        print(age.years)  # 4.0

    Note:
        - All calculations use full datetimes (date and time), not just dates.
        - The class is designed for correctness and flexibility, supporting arbitrary calendar policies and update patterns.
    """

    def __init__(
        self,
        start_time: dt.datetime | float | int,
        end_time: dt.datetime | float | int | None = None,
        cal_policy: CalendarPolicy | None = None,
    ):
        self._start_time: dt.datetime
        self._end_time: dt.datetime
        self.set_times(start_time=start_time, end_time=end_time)
        if cal_policy is None:
            self._cal_policy: CalendarPolicy = CalendarPolicy()
        else:
            self._cal_policy: CalendarPolicy = cal_policy

    @property
    def start_time(self) -> dt.datetime:
        return self._start_time

    @property
    def end_time(self) -> dt.datetime:
        return self._end_time

    def set_times(
        self,
        *,
        start_time: dt.datetime | float | int | None = None,
        end_time: dt.datetime | float | int | None = None,
    ) -> None:
        """
        Update the start and/or end time for this Age instance.

        This method is kwargs-only: you must specify start_time and/or end_time as keyword arguments.
        If a value is None, the previous value is retained.

        Parameters:
            start_time (dt.datetime | float | int | None): New start time. If None, keeps previous value.
            end_time   (dt.datetime | float | int | None): New end time. If None, keeps previous value.

        Type support:
            - dt.datetime: Used directly
            - float/int: Interpreted as a POSIX timestamp

        Raises:
            TypeError: If a provided value is not a supported type
            ValueError: If start_time is not set at least once

        Example:
            age.set_times(start_time=dt.datetime(2020, 1, 1))
            age.set_times(end_time=dt.datetime(2024, 1, 1))
            age.set_times(start_time=1700000000.0)  # POSIX timestamp
        """
        if start_time is not None:
            if isinstance(start_time, (float, int)):
                self._start_time = dt.datetime.fromtimestamp(start_time)
            elif isinstance(start_time, dt.datetime):
                self._start_time = start_time
            else:
                raise TypeError("start_time must be datetime, float, or int")
        elif not hasattr(self, '_start_time'):
            raise ValueError("start_time must be set at least once")

        if end_time is not None:
            if isinstance(end_time, (float, int)):
                self._end_time = dt.datetime.fromtimestamp(end_time)
            elif isinstance(end_time, dt.datetime):
                self._end_time = end_time
            else:
                raise TypeError("end_time must be datetime, float, int, or None")
        elif not hasattr(self, '_end_time'):
            self._end_time = dt.datetime.now()

    # Suggestion: You can use set_times inside __init__ to centralize type handling and validation for start/end times. This makes future updates easier and keeps logic DRY.

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
        """
        Get age in years (approximate - 365.25 days, can be negative).

        Note:
            This calculation uses 365.25 days per year for approximation, which averages leap and non-leap years.
        """
        # Allow negative ages if base_time is before timestamp
        # Uses 365.25 days/year for approximation; does not distinguish leap/non-leap years.
        return self.days / DAYS_PER_YEAR


    @property
    def working_days(self) -> float:
        """
        Calculate the fractional number of working days between start_time and end_time using the calendar policy.

        This method uses full datetimes (date and time), not just dates, for all calculations.
        Partial days are counted based on the time component and business hours in the calendar policy.

        Supports arbitrary calendar policies, including:
        - Non-contiguous workdays (e.g., Mon, Wed, Fri, Sun)
        - Variable business hours per day
        - Irregular holiday schedules
        - Any combination of workdays and holidays as defined in CalendarPolicy

        Algorithm:
        - Iterates from start_time to end_time (inclusive, by date)
        - For each day, checks if it is a workday and not a holiday per cal_policy
        - For valid workdays, calculates the fraction of the business day worked using the time component
        - Handles partial days for first and last day based on business hours
        - Sums all valid fractions to return the total working days (may be fractional)
        - Raises ValueError if start_time > end_time

        Note:
        - This implementation prioritizes correctness and flexibility over efficiency.
        - It is designed to support arbitrary policies where workdays, holidays, and business hours may vary and are not contiguous or regular.
        - Optimization is possible, but correctness is preferred unless efficiency is shown to be a bottleneck.

        Returns:
            float: Total fractional working days in the interval
        """
        # Supports arbitrary calendar policies: workdays, holidays, business hours may be non-contiguous or irregular.
        # Correctness is prioritized over efficiency; optimize only if proven necessary.
        if self.start_time > self.end_time:
            raise ValueError("start_time must not be after end_time")

        cal_policy = self.cal_policy or CalendarPolicy()
        current = self.start_time
        end = self.end_time

        total = 0.0
        while current.date() <= end.date():
            is_workday = cal_policy.is_workday(current) and not cal_policy.is_holiday(current)
            if is_workday:
                # First day
                if current.date() == self.start_time.date():
                    start_dt = self.start_time
                    end_dt = min(end, dt.datetime.combine(current.date(), cal_policy.end_of_business))
                # Last day
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(current.date(), cal_policy.start_of_business)
                    end_dt = end
                # Middle days
                else:
                    start_dt = dt.datetime.combine(current.date(), cal_policy.start_of_business)
                    end_dt = dt.datetime.combine(current.date(), cal_policy.end_of_business)

                # Calculate fraction
                fraction = cal_policy.business_day_fraction(end_dt) - cal_policy.business_day_fraction(start_dt)
                total += max(fraction, 0.0)
            current += dt.timedelta(days=1)
        return total

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
