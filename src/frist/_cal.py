
"""
Calendar-based time window filtering for frist package.

Provides calendar window filtering functionality for Chronoobjects).
"""

import datetime as dt
from typing import TYPE_CHECKING

from ._constants import WEEKDAY_INDEX
from ._util import verify_start_end, in_half_open,in_half_open_date,in_half_open_dt

if TYPE_CHECKING:  # pragma: no cover
    pass




def normalize_weekday(day_spec: str) -> int:
    """Normalize various day-of-week specifications to Python weekday numbers.

    Args:
        day_spec: Day specification as a string

    Returns:
        int: Python weekday number (0=Monday, 1=Tuesday, ..., 6=Sunday)

    Accepts:
        - Full names: 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        - 3-letter abbrev: 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
        - 2-letter abbrev: 'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'
        - Pandas style: 'w-mon', 'w-tue', etc.
        - All case insensitive

    Examples:
        normalize_weekday('monday') -> 0
        normalize_weekday('MON') -> 0
        normalize_weekday('w-sun') -> 6
        normalize_weekday('thu') -> 3
    """
    day_spec = str(day_spec).lower().strip()

    # Remove pandas-style prefix
    if day_spec.startswith("w-"):
        day_spec = day_spec[2:]

    if day_spec in WEEKDAY_INDEX:
        return WEEKDAY_INDEX[day_spec]

    # Generate helpful error message
    valid_examples = [
        "Full: 'monday', 'sunday'",
        "3-letter: 'mon', 'sun', 'tue', 'wed', 'thu', 'fri', 'sat'",
        "2-letter: 'mo', 'su', 'tu', 'we', 'th', 'fr', 'sa'",
        "Pandas: 'w-mon', 'w-sun'",
    ]
    raise ValueError(
        f"Invalid day specification: '{day_spec}'. Valid formats:\n"
        + "\n".join(f"  • {ex}" for ex in valid_examples)
    )




class Cal:
    """Calendar window filtering functionality for direct datetime/timestamp inputs."""

    def __init__(
        self,
        target_dt: dt.datetime | float | int,
        ref_dt: dt.datetime | float | int,
    ) -> None:
        # Convert to datetime if needed
        if isinstance(target_dt, (float, int)):
            self._target_dt = dt.datetime.fromtimestamp(target_dt)
        elif isinstance(target_dt, dt.datetime): # type: ignore # Explicit type check for runtime safety
            self._target_dt = target_dt
        else:
            raise TypeError("target_dt must be datetime, float, or int")

        if isinstance(ref_dt, (float, int)):
            self._ref_dt = dt.datetime.fromtimestamp(ref_dt)
        elif isinstance(ref_dt, dt.datetime): # type: ignore # Explicit type check for runtime safety
            self._ref_dt = ref_dt
        else:
            raise TypeError("ref_dt must be datetime, float, or int")


    @property
    def target_dt(self) -> dt.datetime:
        """Get the target datetime."""
        return self._target_dt
    
    @property
    def ref_dt(self) -> dt.datetime:
        """Get the reference datetime."""
        return self._ref_dt
    



    @verify_start_end
    def in_minutes(self, start: int = 0, end: int = 0) -> bool:
        """
        True if timestamp falls within the minute window(s) from start to end.

        Uses a half-open interval: start_minute <= target_time < end_minute.

        Args:
            start: Minutes from now to start range (negative = past, 0 = current minute, positive = future)
            end: Minutes from now to end range (defaults to start for single minute)

        Examples:
            chrono.cal.in_minutes(0)          # This minute (now)
            chrono.cal.in_minutes(-5)         # 5 minutes ago only
            chrono.cal.in_minutes(-10, -5)    # From 10 minutes ago through 5 minutes ago
            chrono.cal.in_minutes(-30, 0)     # Last 30 minutes through now
        """

        target_time = self.target_dt

        # Calculate the time window boundaries
        start_time = self.ref_dt + dt.timedelta(minutes=start)
        start_minute = start_time.replace(second=0, microsecond=0)

        end_time = self.ref_dt + dt.timedelta(minutes=end)
        # `verify_start_end` already normalizes a single-arg call so `end` is
        # the exclusive offset. Do not advance the boundary here or we'll
        # double-count the end unit.
        end_minute = end_time.replace(second=0, microsecond=0)

        return in_half_open_dt(start_minute, target_time, end_minute)
        
    @verify_start_end
    def in_hours(self, start: int = 0, end: int = 0) -> bool:
        """
        True if timestamp falls within the hour window(s) from start to end.

        Uses a half-open interval: start_hour <= target_time < end_hour.

        Args:
            start: Hours from now to start range (negative = past, 0 = current hour, positive = future)
            end: Hours from now to end range (defaults to start for single hour)

        Examples:
            chrono.cal.in_hours(0)          # This hour (now)
            chrono.cal.in_hours(-2)         # 2 hours ago only
            chrono.cal.in_hours(-6, -1)     # From 6 hours ago through 1 hour ago
            chrono.cal.in_hours(-24, 0)     # Last 24 hours through now
        """

        target_time = self.target_dt

        # Calculate the time window boundaries
        start_time = self.ref_dt + dt.timedelta(hours=start)
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)

        end_time = self.ref_dt + dt.timedelta(hours=end)
        # See note above: `end` is already exclusive when normalized by the
        # decorator; do not add an extra hour.
        end_hour = end_time.replace(minute=0, second=0, microsecond=0)

        return in_half_open_dt(start_hour, target_time, end_hour)

    @verify_start_end
    def in_days(self, start: int = 0, end: int = 0) -> bool:
        """True if timestamp falls within the day window(s) from start to end.

        Args:
            start: Days from reference to start range (negative = past, 0 = today, positive = future)
            end: Days from reference to end range (defaults to start for single day)

        Examples:
            cal.in_days(0)          # Today only
            cal.in_days(-1)         # Yesterday only
            cal.in_days(-7, -1)     # From 7 days ago through yesterday
            cal.in_days(-30, 0)     # Last 30 days through today
        """

        target_date = self.target_dt.date()

        # Calculate the date range boundaries
        start_date = (self.ref_dt + dt.timedelta(days=start)).date()
        # Half-open semantics for days: `end` is exclusive (the decorator
        # supplies end=start+1 for single-arg calls), so use the date for
        # the exclusive end directly without adding an extra day here.
        end_date = (self.ref_dt + dt.timedelta(days=end)).date()

        return in_half_open_date(start_date, target_date, end_date)

    def _month_index(self,d: dt.datetime) -> int:
        """Get a monatonic month index for comparison. (why didn't I think of this?)"""
        return d.year * 12 + d.month

    @verify_start_end
    def in_months(self,start: int = 0, end: int = 0) -> bool:
        """Return whether target falls in calendar months from start..end offsets.

        The implementation compares numeric month indices:
            idx = year * 12 + month

        Args:
            start: Month offset from reference to start (negative = past).
            end: Month offset from reference to end.

        Returns:
            bool: True if target's month index falls between start and end offsets.

        Examples:
            # Two full months before reference:
            cal.in_months(-2, -1)
        """
        target_idx: int = self._month_index(self.target_dt)
        start_idx = self._month_index(self.ref_dt) + start
        end_idx = self._month_index(self.ref_dt) + end

        # Half-open semantics for months: `end_idx` is the exclusive month
        # index (decorator normalization ensures single-arg calls behave as
        # a single unit window). Compare numeric month indices directly.
        return in_half_open(start_idx, target_idx, end_idx)



    @verify_start_end
    def in_quarters(self, start: int = 0, end: int = 0) -> bool:
        """
        True if timestamp falls within the quarter window(s) from start to end.

        Uses a half-open interval: start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1).

        Args:
            start: Quarters from now to start range (negative = past, 0 = this quarter, positive = future)
            end: Quarters from now to end range (defaults to start for single quarter)

        Examples:
            chrono.cal.in_quarters(0)          # This quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
            chrono.cal.in_quarters(-1)         # Last quarter
            chrono.cal.in_quarters(-4, -1)     # From 4 quarters ago through last quarter
            chrono.cal.in_quarters(-8, 0)      # Last 8 quarters through this quarter
        """

        target_time = self.target_dt
        base_time = self.ref_dt

        # Use a monotonic quarter index (year * 4 + (quarter-1)) so we can
        # compare quarters with integer arithmetic (consistent with
        # `_month_index`). This avoids tuple allocations and is slightly
        # simpler to reason about.
        base_quarter = ((base_time.month - 1) // 3)  # 0..3 offset within year
        base_year = base_time.year

        def quarter_index_for_offset(offset: int) -> int:
            # Monotonic index where Q1 of year Y -> Y*4 + 0
            return base_year * 4 + base_quarter + offset

        start_idx = quarter_index_for_offset(start)
        end_idx = quarter_index_for_offset(end)

        # Target's monotonic quarter index
        target_quarter = ((target_time.month - 1) // 3)
        target_year = target_time.year
        target_idx = target_year * 4 + target_quarter

        # Check if target falls within the quarter range using half-open semantics
        return in_half_open(start_idx, target_idx, end_idx)

    @verify_start_end
    def in_years(self, start: int = 0, end: int = 0) -> bool:
        """True if timestamp falls within the year window(s) from start to end.

        Args:
            start: Years from now to start range (negative = past, 0 = this year, positive = future)
            end: Years from now to end range (defaults to start for single year)

        Examples:
            chrono.cal.in_years(0)          # This year
            chrono.cal.in_years(-1)         # Last year only
            chrono.cal.in_years(-5, -1)     # From 5 years ago through last year
            chrono.cal.in_years(-10, 0)     # Last 10 years through this year
        """

        target_year = self.target_dt.year
        base_year = self.ref_dt.year

        # Calculate year range boundaries
        start_year = base_year + start
        end_year = base_year + end

        # Use half-open semantics for years: `end_year` is exclusive. The
        # decorator already makes single-arg calls represent a single-year
        # half-open interval (start..start+1), so no extra shifting is
        # required here.
        return in_half_open(start_year, target_year, end_year)
    
    @verify_start_end
    def in_weeks(
        self, start: int = 0, end: int = 0, week_start: str = "monday"
    ) -> bool:
        """True if timestamp falls within the week window(s) from start to end.

        Args:
            start: Weeks from now to start range (negative = past, 0 = current week, positive = future)
            end: Weeks from now to end range (defaults to start for single week)
            week_start: Week start day (default: 'monday' for ISO weeks)
                - 'monday'/'mon'/'mo' (ISO 8601 default)
                - 'sunday'/'sun'/'su' (US convention)
                - Supports full names, abbreviations, pandas style ('w-mon')
                - Case insensitive

        Examples:
            chrono.cal.in_weeks(0)                     # This week (Monday start)
            chrono.cal.in_weeks(-1, week_start='sun')  # Last week (Sunday start)
            chrono.cal.in_weeks(-4, 0)                 # Last 4 weeks through this week
            chrono.cal.in_weeks(-2, -1, 'sunday')      # 2-1 weeks ago (Sunday weeks)
        """

        week_start_day = normalize_weekday(week_start)

        target_date = self.target_dt.date()
        base_date = self.ref_dt.date()

        # Calculate the start of the current week based on week_start_day
        days_since_week_start = (base_date.weekday() - week_start_day) % 7
        current_week_start = base_date - dt.timedelta(days=days_since_week_start)

        # Calculate week boundaries
        start_week_start = current_week_start + dt.timedelta(weeks=start)
        end_week_start = current_week_start + dt.timedelta(weeks=end)
        # Half-open semantics for weeks: `end_week_start` is already the
        # exclusive start-of-week produced by the normalized `end` value;
        # do not add an extra week here.
        end_week_exclusive = end_week_start

        return in_half_open_date(start_week_start, target_date, end_week_exclusive)

    # Shortcuts for common calendar windows

    @property
    def is_today(self) -> bool:
        """Return True if target is in the same calendar day as the reference.

        Uses calendar-aligned half-open semantics for the day window:
        start_of_day <= target < start_of_next_day.

        Shortcut: equivalent to calling self.in_days(0).
        """
        return self.in_days(0)

    @property
    def is_yesterday(self) -> bool:
        """Return True if target is in the calendar day immediately before the reference.

        Shortcut: equivalent to calling self.in_days(-1).
        """
        return self.in_days(-1)

    @property
    def is_tomorrow(self) -> bool:
        """Return True if target is in the calendar day immediately after the reference.

        Shortcut: equivalent to calling self.in_days(1).
        """
        return self.in_days(1)

    @property
    def is_last_week(self) -> bool:
        """Return True if target is in the last week from the reference.

        Week start follows the default used by in_weeks (Monday).
        Shortcut: equivalent to calling self.in_weeks(-1).
        """
        return self.in_weeks(-1)
    
    @property
    def is_this_week(self) -> bool:
        """Return True if target is in the same week as the reference.

        Week start follows the default used by in_weeks (Monday).
        Shortcut: equivalent to calling self.in_weeks(0).
        """
        return self.in_weeks(0)

    @property
    def is_next_week(self) -> bool:
        """Return True if target is in the week immediately following the reference week.

        Shortcut: equivalent to calling self.in_weeks(1).
        """
        return self.in_weeks(1)

    @property
    def is_last_month(self) -> bool:
        """Return True if target is in the last calendar month as the reference.

        Shortcut: equivalent to calling self.in_months(-1).
        """
        return self.in_months(-1)
    @property
    def is_this_month(self) -> bool:
        """Return True if target is in the same calendar month as the reference.

        Shortcut: equivalent to calling self.in_months(0).
        """
        return self.in_months(0)

    @property
    def is_next_month(self) -> bool:
        """Return True if target is in the calendar month immediately after the reference month.

        Shortcut: equivalent to calling self.in_months(1).
        """
        return self.in_months(1)

    @property
    def is_this_quarter(self) -> bool:
        """Return True if target is in the same calendar quarter as the reference.

        Quarters are calendar aligned (Q1: Jan–Mar, Q2: Apr–Jun, Q3: Jul–Sep, Q4: Oct–Dec).
        Shortcut: equivalent to calling self.in_quarters(0).
        """
        return self.in_quarters(0)

    @property
    def is_last_quarter(self) -> bool:
        """Return True if target is in the quarter immediately before the reference.

        Shortcut: equivalent to calling self.in_quarters(-1).
        """
        return self.in_quarters(-1)

    @property
    def is_next_quarter(self) -> bool:
        """Return True if target is in the quarter immediately after the reference quarter.

        Shortcut: equivalent to calling self.in_quarters(1).
        """
        return self.in_quarters(1)

    @property
    def is_this_year(self) -> bool:
        """Return True if target is in the same calendar year as the reference.

        Shortcut: equivalent to calling self.in_years(0).
        """
        return self.in_years(0)

    @property
    def is_next_year(self) -> bool:
        """Return True if target is in the calendar year immediately after the reference.

        Shortcut: equivalent to calling self.in_years(1).
        """
        return self.in_years(1)

    @property
    def is_last_year(self) -> bool:
        """Return True if target is in the calendar year immediately before the reference.

        Shortcut: equivalent to calling self.in_years(-1).
        """
        return self.in_years(-1)