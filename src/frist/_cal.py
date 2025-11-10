
"""
Calendar-based time window filtering for Frist package.

Provides calendar window filtering functionality that works with any object
having datetime and base_time properties (Time or Frist objects).
"""

import datetime as dt
from typing import TYPE_CHECKING, Protocol

from ._constants import WEEKDAY_INDEX

if TYPE_CHECKING:  # pragma: no cover
    pass


class TimeSpan(Protocol):
    """Protocol for objects that represent a time span between two datetime points."""

    @property
    def target_dt(self) -> dt.datetime:
        """The target datetime being analyzed."""
        raise NotImplementedError

    @property
    def ref_dt(self) -> dt.datetime:
        """The reference datetime for span calculations."""
        raise NotImplementedError



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
    """Calendar window filtering functionality for TimeSpan objects."""

    def __init__(self, time_span: TimeSpan, fy_start_month: int = 1, holidays: set[str] | None = None) -> None:
        """Initialize with a TimeSpan object to provide calendar filtering methods."""
        self.time_span: TimeSpan = time_span
        self.fy_start_month: int = fy_start_month
        self.holidays: set[str] = holidays if holidays is not None else set()





    @property
    def holiday(self) -> bool:
        """Return True if dt_val is a holiday (in holidays set)."""
        date_str = self.dt_val.strftime('%Y-%m-%d')
        return date_str in self.holidays
    @property
    def fiscal_year(self) -> int:
        """Return the fiscal year for dt_val based on fy_start_month."""
        month = self.dt_val.month
        year = self.dt_val.year
        if month >= self.fy_start_month:
            return year
        else:
            return year - 1

    @property
    def fiscal_quarter(self) -> int:
        """Return the fiscal quarter for dt_val based on fy_start_month."""
        month = self.dt_val.month
        offset = (month - self.fy_start_month) % 12
        return (offset // 3) + 1

    @property
    def dt_val(self) -> dt.datetime:
        """Get target datetime from the time span."""
        return self.time_span.target_dt

    @property
    def base_time(self) -> dt.datetime:
        """Get reference datetime from the time span."""
        return self.time_span.ref_dt

    def in_minutes(self, start: int = 0, end: int | None = None) -> bool:
        """
        True if timestamp falls within the minute window(s) from start to end.

        Uses a half-open interval: start_minute <= target_time < end_minute.

        Args:
            start: Minutes from now to start range (negative = past, 0 = current minute, positive = future)
            end: Minutes from now to end range (defaults to start for single minute)

        Examples:
            zeit.cal.in_minutes(0)          # This minute (now)
            zeit.cal.in_minutes(-5)         # 5 minutes ago only
            zeit.cal.in_minutes(-10, -5)    # From 10 minutes ago through 5 minutes ago
            zeit.cal.in_minutes(-30, 0)     # Last 30 minutes through now
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        target_time = self.dt_val

        # Calculate the time window boundaries
        start_time = self.base_time + dt.timedelta(minutes=start)
        start_minute = start_time.replace(second=0, microsecond=0)

        end_time = self.base_time + dt.timedelta(minutes=end)
        end_minute = end_time.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)

        return start_minute <= target_time < end_minute

    def in_hours(self, start: int = 0, end: int | None = None) -> bool:
        """
        True if timestamp falls within the hour window(s) from start to end.

        Uses a half-open interval: start_hour <= target_time < end_hour.

        Args:
            start: Hours from now to start range (negative = past, 0 = current hour, positive = future)
            end: Hours from now to end range (defaults to start for single hour)

        Examples:
            zeit.cal.in_hours(0)          # This hour (now)
            zeit.cal.in_hours(-2)         # 2 hours ago only
            zeit.cal.in_hours(-6, -1)     # From 6 hours ago through 1 hour ago
            zeit.cal.in_hours(-24, 0)     # Last 24 hours through now
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        target_time = self.dt_val

        # Calculate the time window boundaries
        start_time = self.base_time + dt.timedelta(hours=start)
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)

        end_time = self.base_time + dt.timedelta(hours=end)
        end_hour = end_time.replace(minute=0, second=0, microsecond=0) + dt.timedelta(
            hours=1
        )

        return start_hour <= target_time < end_hour

    def in_days(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the day window(s) from start to end.

        Args:
            start: Days from now to start range (negative = past, 0 = today, positive = future)
            end: Days from now to end range (defaults to start for single day)

        Examples:
            zeit.cal.in_days(0)          # Today only
            zeit.cal.in_days(-1)         # Yesterday only
            zeit.cal.in_days(-7, -1)     # From 7 days ago through yesterday
            zeit.cal.in_days(-30, 0)     # Last 30 days through today
        """
        if end is None:
            end = start

        if start > end:
            msg = f"start ({start}) must not be greater than end ({end})"
            raise ValueError(msg)

        target_date = self.dt_val.date()

        # Calculate the date range boundaries
        start_date = (self.base_time + dt.timedelta(days=start)).date()
        end_date = (self.base_time + dt.timedelta(days=end)).date()

        return start_date <= target_date <= end_date

    def in_months(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the month window(s) from start to end.

        Args:
            start: Months from now to start range (negative = past, 0 = this month, positive = future)
            end: Months from now to end range (defaults to start for single month)

        Examples:
            zeit.cal.in_months(0)          # This month
            zeit.cal.in_months(-1)         # Last month only
            zeit.cal.in_months(-6, -1)     # From 6 months ago through last month
            zeit.cal.in_months(-12, 0)     # Last 12 months through this month
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        target_time = self.dt_val
        base_year = self.base_time.year
        base_month = self.base_time.month

        # Calculate the start month (earliest)
        start_month = base_month + start
        start_year = base_year
        while start_month <= 0:
            start_month += 12
            start_year -= 1
        while start_month > 12:
            start_month -= 12
            start_year += 1

        # Calculate the end month (latest)
        end_month = base_month + end
        end_year = base_year
        while end_month <= 0:
            end_month += 12
            end_year -= 1
        while end_month > 12:
            end_month -= 12
            end_year += 1

        # Convert months to a comparable format (year * 12 + month)
        file_month_index = target_time.year * 12 + target_time.month
        start_month_index = start_year * 12 + start_month
        end_month_index = end_year * 12 + end_month

        return start_month_index <= file_month_index <= end_month_index

    def in_quarters(self, start: int = 0, end: int | None = None) -> bool:
        """
        True if timestamp falls within the quarter window(s) from start to end.

        Uses a half-open interval: start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1).

        Args:
            start: Quarters from now to start range (negative = past, 0 = this quarter, positive = future)
            end: Quarters from now to end range (defaults to start for single quarter)

        Examples:
            zeit.cal.in_quarters(0)          # This quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
            zeit.cal.in_quarters(-1)         # Last quarter
            zeit.cal.in_quarters(-4, -1)     # From 4 quarters ago through last quarter
            zeit.cal.in_quarters(-8, 0)      # Last 8 quarters through this quarter
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        target_time = self.dt_val
        base_time = self.base_time

        # Get current quarter (1-4) and year
        current_quarter = ((base_time.month - 1) // 3) + 1
        current_year = base_time.year

        def normalize_quarter_year(offset: int) -> tuple[int, int]:
            total_quarters = (current_year * 4 + current_quarter + offset - 1)
            year = total_quarters // 4
            quarter = (total_quarters % 4) + 1
            return year, quarter

        start_year, start_quarter = normalize_quarter_year(start)
        end_year, end_quarter = normalize_quarter_year(end)

        # Get target's quarter
        target_quarter = ((target_time.month - 1) // 3) + 1
        target_year = target_time.year

        # Use tuple comparison for (year, quarter)
        target_tuple = (target_year, target_quarter)
        start_tuple = (start_year, start_quarter)
        end_tuple = (end_year, end_quarter)

        # Check if target falls within the quarter range: start <= target < end
        return start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1)

    def in_years(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the year window(s) from start to end.

        Args:
            start: Years from now to start range (negative = past, 0 = this year, positive = future)
            end: Years from now to end range (defaults to start for single year)

        Examples:
            zeit.cal.in_years(0)          # This year
            zeit.cal.in_years(-1)         # Last year only
            zeit.cal.in_years(-5, -1)     # From 5 years ago through last year
            zeit.cal.in_years(-10, 0)     # Last 10 years through this year
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        target_year = self.dt_val.year
        base_year = self.base_time.year

        # Calculate year range boundaries
        start_year = base_year + start
        end_year = base_year + end

        return start_year <= target_year <= end_year

    def in_weeks(
        self, start: int = 0, end: int | None = None, week_start: str = "monday"
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
            zeit.cal.in_weeks(0)                     # This week (Monday start)
            zeit.cal.in_weeks(-1, week_start='sun')  # Last week (Sunday start)
            zeit.cal.in_weeks(-4, 0)                 # Last 4 weeks through this week
            zeit.cal.in_weeks(-2, -1, 'sunday')      # 2-1 weeks ago (Sunday weeks)
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        # Normalize the week start day
        week_start_day = normalize_weekday(week_start)

        target_date = self.dt_val.date()
        base_date = self.base_time.date()

        # Calculate the start of the current week based on week_start_day
        days_since_week_start = (base_date.weekday() - week_start_day) % 7
        current_week_start = base_date - dt.timedelta(days=days_since_week_start)

        # Calculate week boundaries
        start_week_start = current_week_start + dt.timedelta(weeks=start)
        end_week_start = current_week_start + dt.timedelta(weeks=end)
        end_week_end = end_week_start + dt.timedelta(
            days=6
        )  # End of week (6 days after start)

        return start_week_start <= target_date <= end_week_end


    def in_fiscal_quarters(self, start: int = 0, end: int | None = None) -> bool:
        """
        True if timestamp falls within the fiscal quarter window(s) from start to end.

        Uses a half-open interval: start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1).

        Args:
            start: Fiscal quarters from now to start range (negative = past, 0 = this fiscal quarter, positive = future)
            end: Fiscal quarters from now to end range (defaults to start for single fiscal quarter)

        Examples:
            zeit.cal.in_fiscal_quarters(0)          # This fiscal quarter
            zeit.cal.in_fiscal_quarters(-1)         # Last fiscal quarter
            zeit.cal.in_fiscal_quarters(-4, -1)     # From 4 fiscal quarters ago through last fiscal quarter
            zeit.cal.in_fiscal_quarters(-8, 0)      # Last 8 fiscal quarters through this fiscal quarter
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        base_time = self.base_time
        fy_start_month = self.fy_start_month

        fy = Cal.get_fiscal_year(base_time, fy_start_month)
        fq = Cal.get_fiscal_quarter(base_time, fy_start_month)

        def normalize_fiscal_quarter_year(offset: int) -> tuple[int, int]:
            total_quarters = (fy * 4 + fq + offset - 1)
            year = total_quarters // 4
            quarter = (total_quarters % 4) + 1
            return year, quarter

        start_year, start_quarter = normalize_fiscal_quarter_year(start)
        end_year, end_quarter = normalize_fiscal_quarter_year(end)

        target_fy = Cal.get_fiscal_year(self.dt_val, fy_start_month)
        target_fq = Cal.get_fiscal_quarter(self.dt_val, fy_start_month)

        target_tuple = (target_fy, target_fq)
        start_tuple = (start_year, start_quarter)
        end_tuple = (end_year, end_quarter)

        return start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1)


    def in_fiscal_years(self, start: int = 0, end: int | None = None) -> bool:
        """
        True if timestamp falls within the fiscal year window(s) from start to end.

        Uses a half-open interval: start_year <= target_year < end_year + 1.

        Args:
            start: Fiscal years from now to start range (negative = past, 0 = this fiscal year, positive = future)
            end: Fiscal years from now to end range (defaults to start for single fiscal year)

        Examples:
            zeit.cal.in_fiscal_years(0)          # This fiscal year
            zeit.cal.in_fiscal_years(-1)         # Last fiscal year
            zeit.cal.in_fiscal_years(-5, -1)     # From 5 fiscal years ago through last fiscal year
            zeit.cal.in_fiscal_years(-10, 0)     # Last 10 fiscal years through this fiscal year
        """
        if end is None:
            end = start

        if start > end:
            raise ValueError(f"start ({start}) must not be greater than end ({end})")

        base_time = self.base_time
        fy_start_month = self.fy_start_month

        fy = Cal.get_fiscal_year(base_time, fy_start_month)
        start_year = fy + start
        end_year = fy + end

        target_fy = Cal.get_fiscal_year(self.dt_val, fy_start_month)

        return start_year <= target_fy < end_year + 1
    @staticmethod
    def get_fiscal_year(dt: dt.datetime, fy_start_month: int) -> int:
        """Return the fiscal year for a given datetime and fiscal year start month."""
        return dt.year if dt.month >= fy_start_month else dt.year - 1

    @staticmethod
    def get_fiscal_quarter(dt: dt.datetime, fy_start_month: int) -> int:
        """Return the fiscal quarter for a given datetime and fiscal year start month."""
        offset = (dt.month - fy_start_month) % 12 if dt.month >= fy_start_month else (dt.month + 12 - fy_start_month) % 12
        return (offset // 3) + 1
