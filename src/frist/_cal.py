
"""
Calendar-based time window filtering for frist package.

Provides calendar window filtering functionality for Chronoobjects).
"""


import functools

import datetime as dt
from typing import TYPE_CHECKING


from ._constants import WEEKDAY_INDEX

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




def verify_start_end(func):
    """Decorator to ensure start <= end for in_* methods."""
    @functools.wraps(func)
    def wrapper(self: Any, start: int = 0, end: int | None = None, *args: Any, **kwargs: Any) -> Any:
        if end is None:
            end = start
        if start > end:
            func_name = getattr(func, "__name__", repr(func))
            raise ValueError(f"{func_name}: start ({start}) must not be greater than end ({end})")
        return func(self, start, end, *args, **kwargs)
    return wrapper


class Cal:

    """Calendar window filtering functionality for direct datetime/timestamp inputs."""

    def __init__(
        self,
        target_dt: dt.datetime | float | int,
        ref_dt: dt.datetime | float | int,
        fy_start_month: int = 1,
        holidays: set[str] | None = None,
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

        self.fy_start_month: int = fy_start_month
        self.holidays: set[str] = holidays if holidays is not None else set()


    @property
    def target_dt(self) -> dt.datetime:
        """Get the target datetime."""
        return self._target_dt
    
    @property
    def ref_dt(self) -> dt.datetime:
        """Get the reference datetime."""
        return self._ref_dt
    
    @property
    def holiday(self) -> bool:
        """Return True if target_dt is a holiday (in holidays set)."""
        date_str = self.target_dt.strftime('%Y-%m-%d')
        return date_str in self.holidays

    @property
    def fiscal_year(self) -> int:
        """Return the fiscal year for target_dt based on fy_start_month."""
        month = self.target_dt.month
        year = self.target_dt.year
        if month >= self.fy_start_month:
            return year
        else:
            return year - 1

    @property
    def fiscal_quarter(self) -> int:
        """Return the fiscal quarter for target_dt based on fy_start_month."""
        month = self.target_dt.month
        offset = (month - self.fy_start_month) % 12
        return (offset // 3) + 1


    @verify_start_end
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

        target_time = self.target_dt

        # Calculate the time window boundaries
        start_time = self.ref_dt + dt.timedelta(minutes=start)
        start_minute = start_time.replace(second=0, microsecond=0)

        end_time = self.ref_dt + dt.timedelta(minutes=int(end))
        end_minute = end_time.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)

        return start_minute <= target_time < end_minute

    @verify_start_end
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

        target_time = self.target_dt

        # Calculate the time window boundaries
        start_time = self.ref_dt + dt.timedelta(hours=start)
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)

        end_time = self.ref_dt + dt.timedelta(hours=int(end))
        end_hour = end_time.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=1)

        return start_hour <= target_time < end_hour

    @verify_start_end
    def in_days(self, start: int = 0, end: int | None = None) -> bool:
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
        end_date = (self.ref_dt + dt.timedelta(days=int(end))).date()

        return start_date <= target_date <= end_date


    @verify_start_end
    def in_workdays(self, start: int = 0, end: int | None = None) -> bool:
        """
        True if target_dt falls within the working day window(s) from start to end,
        counting only working days (Monday-Friday, not holidays).

        The window is defined by moving exactly `start` and `end` working days from ref_dt,
        skipping weekends and holidays. The check is inclusive: start_workday <= target_dt <= end_workday.

        Args:
            start: Working days from reference to start range (negative = past, 0 = today, positive = future)
            end: Working days from reference to end range (defaults to start for single working day)

        Examples:
            cal.in_workdays(0)          # Today only, if today is a working day
            cal.in_workdays(-1)         # Previous working day only
            cal.in_workdays(-5, 5)      # From 5 working days ago through 5 working days ahead
        """

        ref_date = self.ref_dt.date()
        target_date = self.target_dt.date()
        holidays = self.holidays

        def move_workdays(date: dt.date, n: int) -> dt.date:
            """Move n working days from date, skipping weekends and holidays."""
            step = 1 if n > 0 else -1
            count = 0
            current = date
            while count < abs(n):
                current += dt.timedelta(days=step)
                if current.weekday() < 5 and current.strftime('%Y-%m-%d') not in holidays:
                    count += 1
            return current

        start_workday = move_workdays(ref_date, start)
        end_workday = move_workdays(ref_date, int(end))

        # Ensure correct ordering
        if start_workday > end_workday:
            start_workday, end_workday = end_workday, start_workday

        # Target must be a workday (Mon-Fri, not holiday)
        is_workday = (
            target_date.weekday() < 5 and target_date.strftime('%Y-%m-%d') not in holidays
        )
        return is_workday and (start_workday <= target_date <= end_workday)


    @verify_start_end
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

        target_time = self.target_dt
        base_year = self.ref_dt.year
        base_month = self.ref_dt.month

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
        end_month = base_month + int(end)
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

    @verify_start_end
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

        target_time = self.target_dt
        base_time = self.ref_dt

        # Get current quarter (1-4) and year
        current_quarter = ((base_time.month - 1) // 3) + 1
        current_year = base_time.year

        def normalize_quarter_year(offset: int) -> tuple[int, int]:
            total_quarters = (current_year * 4 + current_quarter + offset - 1)
            year = total_quarters // 4
            quarter = (total_quarters % 4) + 1
            return year, quarter

        start_year, start_quarter = normalize_quarter_year(start)
        end_year, end_quarter = normalize_quarter_year(int(end))

        # Get target's quarter
        target_quarter = ((target_time.month - 1) // 3) + 1
        target_year = target_time.year

        # Use tuple comparison for (year, quarter)
        target_tuple = (target_year, target_quarter)
        start_tuple = (start_year, start_quarter)
        end_tuple = (end_year, end_quarter)

        # Check if target falls within the quarter range: start <= target < end
        return start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1)

    @verify_start_end
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

        target_year = self.target_dt.year
        base_year = self.ref_dt.year

        # Calculate year range boundaries
        start_year = base_year + start
        end_year = base_year + int(end)

        return start_year <= target_year <= end_year
    
    @verify_start_end
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

        week_start_day = normalize_weekday(week_start)

        target_date = self.target_dt.date()
        base_date = self.ref_dt.date()

        # Calculate the start of the current week based on week_start_day
        days_since_week_start = (base_date.weekday() - week_start_day) % 7
        current_week_start = base_date - dt.timedelta(days=days_since_week_start)

        # Calculate week boundaries
        start_week_start = current_week_start + dt.timedelta(weeks=start)
        end_week_start = current_week_start + dt.timedelta(weeks=int(end))
        end_week_end = end_week_start + dt.timedelta(
            days=6
        )  # End of week (6 days after start)

        return start_week_start <= target_date <= end_week_end


    @verify_start_end
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

        fy_start_month = self.fy_start_month

        base_time = self.ref_dt  # <-- FIXED HERE
        fy = Cal.get_fiscal_year(base_time, fy_start_month)
        fq = Cal.get_fiscal_quarter(base_time, fy_start_month)

        def normalize_fiscal_quarter_year(offset: int) -> tuple[int, int]:
            total_quarters = (fy * 4 + fq + offset - 1)
            year = total_quarters // 4
            quarter = (total_quarters % 4) + 1
            return year, quarter

        start_year, start_quarter = normalize_fiscal_quarter_year(start)
        end_year, end_quarter = normalize_fiscal_quarter_year(int(end))

        target_fy = Cal.get_fiscal_year(self.target_dt, fy_start_month)
        target_fq = Cal.get_fiscal_quarter(self.target_dt, fy_start_month)

        target_tuple = (target_fy, target_fq)
        start_tuple = (start_year, start_quarter)
        end_tuple = (end_year, end_quarter)

        return start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1)


    @verify_start_end
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

        fy_start_month = self.fy_start_month

        base_time = self.ref_dt  # <-- FIXED HERE
        fy = Cal.get_fiscal_year(base_time, fy_start_month)
        start_year = fy + start
        end_year = fy + int(end)

        target_fy = Cal.get_fiscal_year(self.target_dt, fy_start_month)

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

    @staticmethod
    def count_working_days(start: dt.date, end: dt.date, holidays: set[str]) -> int:
        """Count working days between start and end dates (inclusive)."""
        count = 0
        current = start
        while current <= end:
            weekday = current.weekday()
            date_str = current.strftime('%Y-%m-%d')
            if weekday < 5 and date_str not in holidays:  # 0-4 are Mon-Fri
                count += 1
            current += dt.timedelta(days=1)
        return count