"""
Age property implementation for frist package.

Handles age calcs in various time units, supports both file-based and standalone usage.
"""

import datetime as dt
import math
import re
from collections.abc import Callable, Sequence
from enum import StrEnum
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


class AgeFormatStyle(StrEnum):
    """Output style for ``Age.format``: full unit names or the short labels."""

    VERBOSE = "verbose"
    COMPACT = "compact"


AGE_FORMAT_STYLE_VALUES: tuple[str, ...] = tuple(m.value for m in AgeFormatStyle)


def coerce_age_format_style(value: AgeFormatStyle | str) -> AgeFormatStyle:
    """
    Return a AgeFormatStyle from a AgeFormatStyle or its string value.

    Raises ValueError for invalid inputs, naming the valid values.
    """
    try:
        return AgeFormatStyle(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid style value: {value!r}. Valid: {AGE_FORMAT_STYLE_VALUES}"
        ) from exc


class Age:
    """
    Property class for handling age calculations in various time units.

    Features:
        - Computes age and duration between two datetimes, timestamps, or number values.
        - Supports flexible initialization: accepts dt.datetime, dt.date, float, or int
          for start and end times.
        - Provides properties for age in microseconds, milliseconds, seconds, minutes,
          hours, days, weeks, months and years, plus calendar-precise months and years.
        - Represents bare durations (no real endpoints) via ``from_seconds`` and
          ``from_timedelta``.
        - Formats itself in the most appropriate unit via ``format``, using the
          ``PLURAL_UNITS`` table (the default: a unit is used only once two of it have
          elapsed, so a value is never 1.x), ``AGE_UNITS`` (humanize-style rounding) or
          ``DURATION_UNITS`` (clock boundaries, for measurements), with an optional
          ``now`` threshold.
        - Prints either the full unit names (``AgeFormatStyle.VERBOSE`` or ``"verbose"``, the
          default) or the short labels in ``COMPACT_LABELS`` (``AgeFormatStyle.COMPACT`` or
          ``"compact"``: "30h", "13d", "2mo").
        - Floors the display at ``smallest_unit`` (the table's first unit unless named):
          below one of it the text is "< 1 second" / "<1s" rather than a fraction.

    Initialization:
        Age(start_time, end_time=None, formats=None)
        - start_time: TimeLike (dt.datetime, dt.date, float, int, or str) (required)
        - end_time: TimeLike or None (defaults to now)
        - formats: list[str] or None (custom datetime formats for string parsing)

        Age.from_seconds(seconds) / Age.from_timedelta(delta)
        - A duration with no meaningful start/end; both are synthesized from a fixed
          naive anchor (2000-01-01) so the Unix epoch and local timezone never matter.

    Example:
        age = Age(dt.datetime(2020, 1, 1), dt.datetime(2024, 1, 1))
        print(age.years)  # 4.0
        print(age.format())  # "4.00 years"

    Note:
        - All calculations use full datetimes (date and time); dates are converted to
          datetimes at midnight.
        - Civil time: naive datetimes are wall-clock readings.  Timezone-aware datetimes
          (both in the same zone), POSIX timestamps and ``now`` are instants, so the
          elapsed-time properties are exact across DST changes for them.  Calendar
          fractions (``months_precise`` / ``years_precise``) follow the wall clock.
        - Age is immutable: build a new one to change its endpoints.
    """

    # Naive anchor used by ``from_seconds`` / ``from_timedelta``.  A bare duration has
    # no wall-clock endpoints, so one is invented here instead of routing numbers
    # through ``datetime.fromtimestamp`` (local-time dependent, and negative
    # timestamps raise OSError on Windows).
    _DURATION_ANCHOR: ClassVar[dt.datetime] = dt.datetime(2000, 1, 1)

    # Default table for ``format``: a unit is used only once at least two of it have
    # elapsed, so a value is never 1.x and the plural unit names always read correctly.
    # Same rule as Docker's HumanDuration (``docker ps`` CREATED / STATUS): hours under
    # 48 h, days under 2 weeks, weeks under 2 months, months under 2 years; applied
    # below hours too.  Months and years are the average-length ``months`` / ``years``
    # (30.44 d / 365.25 d) so every handoff lands exactly on 2.00; ``AGE_UNITS`` keeps
    # the calendar-precise months.  The final row is unbounded, so nothing falls
    # through to ``years_precise``.
    PLURAL_UNITS: ClassVar[tuple[UnitRow, ...]] = (
        (120, "seconds", lambda age: age.seconds),
        (120, "minutes", lambda age: age.minutes),
        (48, "hours", lambda age: age.hours),
        (14, "days", lambda age: age.days),
        (2 * DAYS_PER_MONTH / DAYS_PER_WEEK, "weeks", lambda age: age.weeks),  # 8.70
        (24, "months", lambda age: age.months),
        (math.inf, "years", lambda age: age.years),
    )

    # Humanize-style table for ``format``: "how old is X?" rounding, with thresholds
    # taken from the humanize library (45 s / 45 min / 22 h / 26 d / 11 mo).  Anything
    # past the last row is reported in ``years_precise``.
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

    # Output styles for ``format``.  Verbose prints the table's unit names with two
    # decimals; compact prints the short labels below with no decimals and no space,
    # the convention Twitter, Reddit and kubectl use ("30h", "13d", "2mo").  ``parse``
    # reads every compact label back.
    VERBOSE_FMT: ClassVar[str] = "{value:.2f} {unit}"
    COMPACT_FMT: ClassVar[str] = "{value:.0f}{unit}"
    # Text for an age below one of the smallest displayed unit (``smallest_unit``).
    VERBOSE_FLOOR_FMT: ClassVar[str] = "< 1 {unit}"
    COMPACT_FLOOR_FMT: ClassVar[str] = "<1{unit}"
    COMPACT_LABELS: ClassVar[dict[str, str]] = {
        "microseconds": "us",
        "milliseconds": "ms",
        "seconds": "s",
        "minutes": "m",
        "hours": "h",
        "days": "d",
        "weeks": "w",
        "months": "mo",
        "years": "y",
    }

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
        self._elapsed_seconds: float = self._elapsed(start_time, end_time)

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

    def _elapsed(self, start_in: TimeLike, end_in: TimeLike | None) -> float:
        """
        Elapsed seconds between the endpoints, as given to the constructor.

        True elapsed time when both endpoints are instants: timezone-aware datetimes
        (``timestamp()`` honours the zone's UTC offsets and ``fold``), or a POSIX
        timestamp paired with a timestamp or with ``now``.  A naive datetime is a
        wall-clock reading, so a pair involving one is a wall-clock difference; across
        a DST change that differs from real time by the shifted hour.
        """
        start, end = self._start_time, self._end_time
        if start.tzinfo is not None and end.tzinfo is not None:
            return end.timestamp() - start.timestamp()
        if isinstance(start_in, int | float) and (
            end_in is None or isinstance(end_in, int | float)
        ):
            end_ts = end.timestamp() if end_in is None else float(end_in)
            return end_ts - float(start_in)
        return (end - start).total_seconds()

    @property
    def seconds(self) -> float:
        """
        Get age in seconds.

        True elapsed time when both endpoints are instants (timezone-aware datetimes,
        POSIX timestamps, ``now``); a wall-clock difference when a naive datetime is
        involved.
        """
        return self._elapsed_seconds

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

        tz = start.tzinfo
        # If start and end are in the same month
        if start.year == end.year and start.month == end.month:
            month_start = dt.datetime(start.year, start.month, 1, tzinfo=tz)
            next_year, next_month = self._next_month_year(start.year, start.month)
            month_end = dt.datetime(next_year, next_month, 1, tzinfo=tz)
            total_seconds = (month_end - month_start).total_seconds()
            interval_seconds = (end - start).total_seconds()
            return scale * (interval_seconds / total_seconds)

        # First month fraction
        next_year, next_month = self._next_month_year(start.year, start.month)
        start_month_end = dt.datetime(next_year, next_month, 1, tzinfo=tz)
        first_month_seconds = (start_month_end - start).total_seconds()
        start_month_begin = dt.datetime(start.year, start.month, 1, tzinfo=tz)
        total_start_month_seconds = (start_month_end - start_month_begin).total_seconds()
        first_month_fraction = first_month_seconds / total_start_month_seconds

        # Last month fraction
        last_month_start = dt.datetime(end.year, end.month, 1, tzinfo=tz)
        next_year, next_month = self._next_month_year(end.year, end.month)
        last_month_end = dt.datetime(next_year, next_month, 1, tzinfo=tz)
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

        tz = start.tzinfo

        def _fractional_days(dt1: dt.datetime, dt2: dt.datetime) -> float:
            """Calculate fractional days between two datetimes."""
            return (dt2 - dt1).total_seconds() / (24 * 3600)

        # Same year: fraction only
        if start.year == end.year:
            days_in_year = (
                dt.datetime(start.year + 1, 1, 1, tzinfo=tz)
                - dt.datetime(start.year, 1, 1, tzinfo=tz)
            ).days
            return scale * (_fractional_days(start, end) / days_in_year)

        # First year fraction
        end_of_first_yr = dt.datetime(start.year, 12, 31, 23, 59, 59, tzinfo=tz)
        days_in_first_yr = (
            dt.datetime(start.year + 1, 1, 1, tzinfo=tz) - dt.datetime(start.year, 1, 1, tzinfo=tz)
        ).days
        first_year_fraction = _fractional_days(start, end_of_first_yr) / days_in_first_yr

        # Last year fraction
        start_of_last_year = dt.datetime(end.year, 1, 1, tzinfo=tz)
        days_in_last_year = (
            dt.datetime(end.year + 1, 1, 1, tzinfo=tz) - dt.datetime(end.year, 1, 1, tzinfo=tz)
        ).days
        last_year_fraction = _fractional_days(start_of_last_year, end) / days_in_last_year

        # Full years in between
        full_years = end.year - start.year - 1

        return scale * (first_year_fraction + full_years + last_year_fraction)

    def format(
        self,
        units: Sequence[UnitRow] | None = None,
        fmt: str | None = None,
        now: int | float | str | None = None,
        now_text: str = "now",
        style: AgeFormatStyle | str = AgeFormatStyle.VERBOSE,
        smallest_unit: str | None = None,
    ) -> str:
        """
        Return age in the most appropriate units, with customizable unit names and formatting.

        Args:
            units: Sequence of (threshold, unit_name, getter) rows controlling units and
                thresholds; the first row whose getter value satisfies
                ``abs(value) < threshold`` wins.  Defaults to ``Age.PLURAL_UNITS``, where a
                unit is used only once two of it have elapsed, so a value is never 1.x.
                ``Age.AGE_UNITS`` gives humanize-style rounding and
                ``Age.DURATION_UNITS`` clock-boundary rounding for measurements.  If no
                row matches, the age is reported in ``years_precise``.  A single row
                with a huge threshold overrides all formatting.
            fmt: Format string for output, receiving ``value`` and ``unit``.  Defaults to
                ``VERBOSE_FMT`` ("{value:.2f} {unit}") or, for the compact style,
                ``COMPACT_FMT`` ("{value:.0f}{unit}").
            now: Optional "close enough to now" threshold.  A number is seconds; a string
                carries its own unit and is parsed by ``Age.parse`` ("10 s", "1.1 min",
                "100ms").  When ``abs(self.seconds)`` is below it, ``now_text`` is
                returned instead of a formatted value.  The right threshold depends on
                what is being aged (10 s for files, 100 ms for serial traffic), so
                there is no default.
            now_text: Text returned when the ``now`` threshold applies.
            style: ``AgeFormatStyle.VERBOSE`` (the default) prints the table's unit names;
                ``AgeFormatStyle.COMPACT`` prints the short labels in ``COMPACT_LABELS``
                ("30h", "13d", "2mo") and, unless ``fmt`` is given, no decimals and no
                space.  The strings "verbose" / "compact" are accepted too.
            smallest_unit: Smallest unit to display, by its name in the table ("hours").
                Below one of it the result is ``VERBOSE_FLOOR_FMT`` / ``COMPACT_FLOOR_FMT``
                ("< 1 hour" / "<1h"), and the rows below it are never used.  Defaults to
                the table's first unit: seconds for ``PLURAL_UNITS`` and ``AGE_UNITS``,
                microseconds for ``DURATION_UNITS``.

        Example:
            age.format()  # "3.25 hours"
            age.format(style="compact")  # "3h"
            age.format(smallest_unit="hours")  # "< 1 hour" while under an hour
            Age.from_seconds(30 * 3600).format()  # "30.00 hours", not "1.25 days"
            age.format(fmt="{value:.0f}{unit}", units=[...])  # "3h"
            age.format(now="10 s")  # "now" while under 10 seconds old
            Age.from_seconds(0.08).format(units=Age.DURATION_UNITS)  # "80.00 milliseconds"
            # Override all formatting:
            age.format(units=[(1e20, "custom:", lambda self: self.seconds)], fmt="{value} {unit}")

        Note:
            ``PLURAL_UNITS`` hands a unit off at 2 min / 2 h / 48 h / 2 weeks / 2 months /
            2 years, the rule Docker's ``HumanDuration`` uses for ``docker ps``.  Below one
            second it prints "< 1 second" (see ``smallest_unit``), and "1.50 seconds" can
            appear up to two seconds; use ``DURATION_UNITS`` for sub-second measurements.
            ``AGE_UNITS`` keeps the thresholds of the `humanize` library (45 s / 45 min /
            22 h / 26 d / 11 mo):
            https://github.com/jmoiron/humanize/blob/main/src/humanize/time.py
        """
        chosen = coerce_age_format_style(style)
        if fmt is None:
            fmt = self.COMPACT_FMT if chosen is AgeFormatStyle.COMPACT else self.VERBOSE_FMT
        labels: dict[str, str] = self.COMPACT_LABELS if chosen is AgeFormatStyle.COMPACT else {}

        if now is not None:
            now_limit: float = Age.parse(now) if isinstance(now, str) else float(now)
            if abs(self.seconds) < now_limit:
                return now_text

        rows: list[UnitRow] = list(units or self.PLURAL_UNITS)
        if smallest_unit is not None:
            names = [name for _, name, _ in rows]
            if smallest_unit not in names:
                raise ValueError(f"Invalid smallest_unit {smallest_unit!r}. Valid: {tuple(names)}")
            rows = rows[names.index(smallest_unit) :]
        _, floor_unit, floor_getter = rows[0]
        if abs(floor_getter(self)) < 1:
            if chosen is AgeFormatStyle.COMPACT:
                return self.COMPACT_FLOOR_FMT.format(unit=labels.get(floor_unit, floor_unit))
            return self.VERBOSE_FLOOR_FMT.format(unit=self._singular(floor_unit))

        for threshold, unit, getter in rows:
            value = getter(self)
            if abs(value) < threshold:
                return fmt.format(value=value, unit=labels.get(unit, unit))
        value = self.years_precise
        return fmt.format(value=value, unit=labels.get("years", "years"))

    def _singular(self, unit: str) -> str:
        """Singular of a standard unit name for the floor text ("hours" -> "hour")."""
        return unit[:-1] if unit in self.COMPACT_LABELS else unit

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
            "2mo" -> 5260032 seconds (2 months, the compact label)
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
            "mo": SECONDS_PER_MONTH,
            "month": SECONDS_PER_MONTH,
            "months": SECONDS_PER_MONTH,
            "y": SECONDS_PER_YEAR,
            "year": SECONDS_PER_YEAR,
            "years": SECONDS_PER_YEAR,
        }

        if unit not in unit_multipliers:
            raise ValueError(f"Unknown unit: {unit}")

        return value * unit_multipliers[unit]


__all__ = ["Age", "AgeFormatStyle"]

# a1 = Age(dt.datetime(2020,1,1), dt.datetime(2021,1,1))
# print(a1.years_precise)
