"""
Age property implementation for frist package.

Handles age calcs in various time units, supports both file-based and standalone usage.
"""

import datetime as dt
import math
import re
from collections.abc import Callable, Sequence
from typing import ClassVar, Self, TypeAlias

from ._constants import (
    DAYS_PER_MONTH,
    DAYS_PER_WEEK,
    DAYS_PER_YEAR,
    MICROSECONDS_PER_SECOND,
    MILLISECONDS_PER_SECOND,
    SECONDS_PER_DAY,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    SECONDS_PER_MONTH,
    SECONDS_PER_WEEK,
    SECONDS_PER_YEAR,
)
from ._types import TimeLike, time_pair

# One row of a unit table for ``Age.format``: (threshold, unit_name, getter).
# ``format`` walks the rows in order and reports the first whose getter value
# satisfies ``abs(value) < threshold``.
UnitRow: TypeAlias = tuple[float, str, Callable[["Age"], float]]


class Age:
    """
    Property class for handling age calculations in various time units.

    Features:
        - Computes age and duration between two datetimes, timestamps, or number values.
        - Supports flexible initialization: accepts dt.datetime, dt.date, float, or int
          for start and end times.
        - Uses a configurable BizPolicy for business calendar logic (workdays, holidays,
          business hours).
        - Provides properties for age in microseconds, milliseconds, seconds, minutes,
          hours, days, weeks, months, years, and fractional working days.
        - Allows updating start and end times via the `set_times` method (kwargs-only,
          preserves previous values if None).
        - Represents bare durations (no real endpoints) via ``from_seconds`` and
          ``from_timedelta``.
        - Formats itself in the most appropriate unit via ``format``, using either the
          ``AGE_UNITS`` table (humanize-style rounding, the default) or the
          ``DURATION_UNITS`` table (clock boundaries, for measurements), with an
          optional ``now`` threshold.

    Initialization:
        Age(start_time, end_time=None, formats=None)
        - start_time: TimeLike (dt.datetime, dt.date, float, int, or str) (required)
        - end_time: TimeLike or None (defaults to now)
        - formats: list[str] or None (custom datetime formats for string parsing)

        Age.from_seconds(seconds) / Age.from_timedelta(delta)
        - A duration with no meaningful start/end; both are synthesized from a fixed
          naive anchor (2000-01-01) so the Unix epoch and local timezone never matter.

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
        - All calculations use full datetimes (date and time); dates are converted to
          datetimes at midnight.
        - Timezones are not supported.
        - The class is designed for correctness and flexibility, supporting arbitrary
          calendar policies and update patterns.
    """

    # Naive anchor used by ``from_seconds`` / ``from_timedelta``.  A bare duration has
    # no wall-clock endpoints, so one is invented here instead of routing numbers
    # through ``datetime.fromtimestamp`` (local-time dependent, and negative
    # timestamps raise OSError on Windows).
    _DURATION_ANCHOR: ClassVar[dt.datetime] = dt.datetime(2000, 1, 1)

    # Default table for ``format``: "how old is X?" rounding, with thresholds taken
    # from the humanize library (45 s / 45 min / 22 h / 26 d / 11 mo).  Anything past
    # the last row is reported in ``years_precise``.
    AGE_UNITS: ClassVar[tuple[UnitRow, ...]] = (
        (45, "seconds", lambda age: age.seconds),
        (45, "minutes", lambda age: age.minutes),
        (22, "hours", lambda age: age.hours),
        (26, "days", lambda age: age.days),
        (11, "months", lambda age: age.months_precise),
    )

    # Measurement table for ``format``: clock boundaries (1000 / 1000 / 60 / 60 / 24)
    # so 46 s reads "46.00 seconds", never "0.77 minutes".  The final row is
    # unbounded, so long durations stay in days rather than falling through to years.
    DURATION_UNITS: ClassVar[tuple[UnitRow, ...]] = (
        (1000, "microseconds", lambda age: age.microseconds),
        (1000, "milliseconds", lambda age: age.milliseconds),
        (60, "seconds", lambda age: age.seconds),
        (60, "minutes", lambda age: age.minutes),
        (24, "hours", lambda age: age.hours),
        (math.inf, "days", lambda age: age.days),
    )

    def __init__(
        self,
        start_time: TimeLike,
        end_time: TimeLike | None = None,
        formats: list[str] | None = None,
    ):
        self._start_time: dt.datetime
        self._end_time: dt.datetime
        self._start_time, self._end_time = time_pair(
            start_time=start_time, end_time=end_time, formats__=formats
        )

    @classmethod
    def from_timedelta(cls, delta: dt.timedelta) -> Self:
        """
        Build an Age representing a bare duration.

        A duration has no meaningful start or end, so both are synthesized from a fixed
        naive anchor (2000-01-01 00:00).  Elapsed-time properties (``seconds``,
        ``hours``, ``days``, ...) and ``format`` behave exactly as for any other Age;
        the calendar-aware ``months_precise`` / ``years_precise`` are measured from
        that anchor.  Negative deltas are allowed and yield negative ages.

        Args:
            delta: The duration to represent.

        Returns:
            Age: An Age whose ``seconds`` equals ``delta.total_seconds()``.

        Example:
            Age.from_timedelta(dt.timedelta(milliseconds=80)).format(units=Age.DURATION_UNITS)
            # "80.00 milliseconds"
        """
        return cls(cls._DURATION_ANCHOR, cls._DURATION_ANCHOR + delta)

    @classmethod
    def from_seconds(cls, seconds: float) -> Self:
        """
        Build an Age representing a bare duration of ``seconds`` seconds.

        See ``from_timedelta`` for the anchoring rules.  Unlike ``Age(0, seconds)``,
        this never touches the Unix epoch or the local timezone, so sub-second and
        negative values work on every platform.  Resolution is one microsecond
        (``datetime.timedelta``'s).

        Args:
            seconds: Duration in seconds; may be fractional or negative.

        Returns:
            Age: An Age whose ``seconds`` equals the argument.

        Example:
            Age.from_seconds(90).format(units=Age.DURATION_UNITS)  # "1.50 minutes"
        """
        return cls.from_timedelta(dt.timedelta(seconds=seconds))

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

    # Note: Age is immutable; no state mutation methods are provided.

    # Suggestion: You can use set_times inside __init__ to centralize type handling and
    # validation for start/end times. Makes future updates easier and keeps logic DRY.

    @property
    def seconds(self) -> float:
        """Get age in seconds."""
        return (self.end_time - self.start_time).total_seconds()

    @property
    def milliseconds(self) -> float:
        """Get age in milliseconds."""
        return self.seconds * MILLISECONDS_PER_SECOND

    @property
    def microseconds(self) -> float:
        """Get age in microseconds."""
        return self.seconds * MICROSECONDS_PER_SECOND

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
        Partial months at start and end are calculated using the actual number of seconds
        in those months (including time portion).
        Full months in between are simply counted as 1.0 each.
        Returns a negative value if start_time > end_time, so that
        Age(start, end).months_precise == -Age(end, start).months_precise.
        """
        # Ensure symmetric negative/positive results for swapped start/end.
        start: dt.datetime
        end: dt.datetime
        scale: float

        if self.start_time <= self.end_time:
            start = self.start_time
            end = self.end_time
            scale = 1.0
        else:
            start = self.end_time
            end = self.start_time
            scale = -1.0

        if start == end:
            return 0.0

        # If start and end are in the same month
        if start.year == end.year and start.month == end.month:
            month_start = dt.datetime(start.year, start.month, 1)
            next_year, next_month = self._next_month_year(start.year, start.month)
            month_end = dt.datetime(next_year, next_month, 1)
            total_seconds = (month_end - month_start).total_seconds()
            interval_seconds = (end - start).total_seconds()
            return scale * (interval_seconds / total_seconds)

        # First month fraction
        next_year, next_month = self._next_month_year(start.year, start.month)
        start_month_end = dt.datetime(next_year, next_month, 1)
        first_month_seconds = (start_month_end - start).total_seconds()
        start_month_begin = dt.datetime(start.year, start.month, 1)
        total_start_month_seconds = (start_month_end - start_month_begin).total_seconds()
        first_month_fraction = first_month_seconds / total_start_month_seconds

        # Last month fraction
        last_month_start = dt.datetime(end.year, end.month, 1)
        next_year, next_month = self._next_month_year(end.year, end.month)
        last_month_end = dt.datetime(next_year, next_month, 1)
        last_month_seconds = (end - last_month_start).total_seconds()
        total_last_month_seconds = (last_month_end - last_month_start).total_seconds()
        last_month_fraction = (
            last_month_seconds / total_last_month_seconds if last_month_seconds > 0 else 0.0
        )

        # Count full months in between
        full_months = 0
        current_year, current_month = self._next_month_year(start.year, start.month)
        while (current_year, current_month) != (end.year, end.month):
            full_months += 1
            current_year, current_month = self._next_month_year(current_year, current_month)

        return scale * (first_month_fraction + full_months + last_month_fraction)

    @property
    def years(self) -> float:
        """
        Get age in years (approximate - 365.25 days, can be negative).

        Note:
            This calculation uses 365.25 days per year for approximation, which
            averages leap and non-leap years.
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
        start: dt.datetime = self.start_time
        end: dt.datetime = self.end_time
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
        end_of_first_yr = dt.datetime(start.year, 12, 31, 23, 59, 59)
        days_in_first_yr = (dt.datetime(start.year + 1, 1, 1) - dt.datetime(start.year, 1, 1)).days
        first_year_fraction = _fractional_days(start, end_of_first_yr) / days_in_first_yr

        # Last year fraction
        start_of_last_year = dt.datetime(end.year, 1, 1)
        days_in_last_year = (dt.datetime(end.year + 1, 1, 1) - dt.datetime(end.year, 1, 1)).days
        last_year_fraction = _fractional_days(start_of_last_year, end) / days_in_last_year

        # Full years in between
        full_years = end.year - start.year - 1

        return scale * (first_year_fraction + full_years + last_year_fraction)

    def format(
        self,
        units: Sequence[UnitRow] | None = None,
        fmt: str = "{value:.2f} {unit}",
        now: int | float | str | None = None,
        now_text: str = "now",
    ) -> str:
        """
        Return age in the most appropriate units, with customizable unit names and formatting.

        Args:
            units: Sequence of (threshold, unit_name, getter) rows controlling units and
                thresholds; the first row whose getter value satisfies
                ``abs(value) < threshold`` wins.  Defaults to ``Age.AGE_UNITS``
                (humanize-style rounding).  ``Age.DURATION_UNITS`` gives clock-boundary
                rounding for measurements.  If no row matches, the age is reported in
                ``years_precise``.  A single row with a huge threshold overrides all
                formatting.
            fmt: Format string for output, receiving ``value`` and ``unit``.
                Default is "{value:.2f} {unit}".
            now: Optional "close enough to now" threshold.  A number is seconds; a string
                carries its own unit and is parsed by ``Age.parse`` ("10 s", "1.1 min",
                "100ms").  When ``abs(self.seconds)`` is below it, ``now_text`` is
                returned instead of a formatted value.  The right threshold depends on
                what is being aged (10 s for files, 100 ms for serial traffic), so
                there is no default.
            now_text: Text returned when the ``now`` threshold applies.

        Example:
            age.format()  # "3.25 hours"
            age.format(fmt="{value:.0f}{unit}", units=[...])  # "3h"
            age.format(now="10 s")  # "now" while under 10 seconds old
            Age.from_seconds(0.08).format(units=Age.DURATION_UNITS)  # "80.00 milliseconds"
            # Override all formatting:
            age.format(units=[(1e20, "custom:", lambda self: self.seconds)], fmt="{value} {unit}")

        Note:
            Default unit transition thresholds are inspired by the `humanize` Python library:
            https://github.com/jmoiron/humanize/blob/main/src/humanize/time.py
            - Seconds → Minutes: 45 seconds
            - Minutes → Hours: 45 minutes
            - Hours → Days: 22 hours
            - Days → Months: 26 days
            - Months → Years: 11 months
        """
        if now is not None:
            now_limit: float = Age.parse(now) if isinstance(now, str) else float(now)
            if abs(self.seconds) < now_limit:
                return now_text

        for threshold, unit, getter in units or self.AGE_UNITS:
            value = getter(self)
            if abs(value) < threshold:
                return fmt.format(value=value, unit=unit)
        value = self.years_precise
        return fmt.format(value=value, unit="years")

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
            "100ms" -> 0.1 seconds (100 milliseconds)
            "250 us" -> 0.00025 seconds (250 microseconds)
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
        unit_multipliers: dict[str, float] = {
            "us": 1 / MICROSECONDS_PER_SECOND,
            "usec": 1 / MICROSECONDS_PER_SECOND,
            "microsecond": 1 / MICROSECONDS_PER_SECOND,
            "microseconds": 1 / MICROSECONDS_PER_SECOND,
            "ms": 1 / MILLISECONDS_PER_SECOND,
            "msec": 1 / MILLISECONDS_PER_SECOND,
            "millisecond": 1 / MILLISECONDS_PER_SECOND,
            "milliseconds": 1 / MILLISECONDS_PER_SECOND,
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

# a1 = Age(dt.datetime(2020,1,1), dt.datetime(2021,1,1))
# print(a1.years_precise)
