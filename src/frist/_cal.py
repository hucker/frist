
"""
Calendar-based time window filtering for frist package.

Provides calendar window filtering functionality for Chrono objects).
"""

import datetime as dt
from typing import TYPE_CHECKING

from ._constants import WEEKDAY_INDEX
from functools import cached_property
from ._ranges import UnitNamespace, MinuteNamespace, HourNamespace, DayNamespace, WeekNamespace, MonthNamespace, QuarterNamespace, YearNamespace
from ._types import TimeLike, to_datetime

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
        target_dt: TimeLike,
        ref_dt: TimeLike,
        formats: list[str] | None = None,
    ) -> None:
        self._target_dt = to_datetime(target_dt, formats)
        self._ref_dt = to_datetime(ref_dt, formats)


    @property
    def target_dt(self) -> dt.datetime:
        """Get the target datetime."""
        return self._target_dt
    
    @property
    def ref_dt(self) -> dt.datetime:
        """Get the reference datetime."""
        return self._ref_dt
    



    # Shortcuts for common calendar windows

    @property
    def is_today(self) -> bool:
        """Return True if target is in the same calendar day as the reference.

        Uses calendar-aligned half-open semantics for the day window:
        start_of_day <= target < start_of_next_day.

        Shortcut: equivalent to calling self.in_days(0).
        """
        return self.day.in_(0)

    @property
    def is_yesterday(self) -> bool:
        """Return True if target is in the calendar day immediately before the reference.

        Shortcut: equivalent to calling self.in_days(-1).
        """
        return self.day.in_(-1)

    @property
    def is_tomorrow(self) -> bool:
        """Return True if target is in the calendar day immediately after the reference.

        Shortcut: equivalent to calling self.in_days(1).
        """
        return self.day.in_(1)

    @property
    def is_last_week(self) -> bool:
        """Return True if target is in the last week from the reference.

        Week start follows the default used by in_weeks (Monday).
        Shortcut: equivalent to calling self.in_weeks(-1).
        """
        return self.week.in_(-1)
    
    @property
    def is_this_week(self) -> bool:
        """Return True if target is in the same week as the reference.

        Week start follows the default used by in_weeks (Monday).
        Shortcut: equivalent to calling self.in_weeks(0).
        """
        return self.week.in_(0)

    @property
    def is_next_week(self) -> bool:
        """Return True if target is in the week immediately following the reference week.

        Shortcut: equivalent to calling self.in_weeks(1).
        """
        return self.week.in_(1)

    @property
    def is_last_month(self) -> bool:
        """Return True if target is in the last calendar month as the reference.

        Shortcut: equivalent to calling self.in_months(-1).
        """
        return self.month.in_(-1)
    @property
    def is_this_month(self) -> bool:
        """Return True if target is in the same calendar month as the reference.

        Shortcut: equivalent to calling self.in_months(0).
        """
        return self.month.in_(0)

    @property
    def is_next_month(self) -> bool:
        """Return True if target is in the calendar month immediately after the reference month.

        Shortcut: equivalent to calling self.in_months(1).
        """
        return self.month.in_(1)

    @property
    def is_this_quarter(self) -> bool:
        """Return True if target is in the same calendar quarter as the reference.

        Quarters are calendar aligned (Q1: Jan–Mar, Q2: Apr–Jun, Q3: Jul–Sep, Q4: Oct–Dec).
        Shortcut: equivalent to calling self.in_quarters(0).
        """
        return self.qtr.in_(0)

    @property
    def is_last_quarter(self) -> bool:
        """Return True if target is in the quarter immediately before the reference.

        Shortcut: equivalent to calling self.in_quarters(-1).
        """
        return self.qtr.in_(-1)

    @property
    def is_next_quarter(self) -> bool:
        """Return True if target is in the quarter immediately after the reference quarter.

        Shortcut: equivalent to calling self.in_quarters(1).
        """
        return self.qtr.in_(1)

    @property
    def is_this_year(self) -> bool:
        """Return True if target is in the same calendar year as the reference.

        Shortcut: equivalent to calling self.in_years(0).
        """
        return self.year.in_(0)

    @property
    def is_next_year(self) -> bool:
        """Return True if target is in the calendar year immediately after the reference.

        Shortcut: equivalent to calling self.in_years(1).
        """
        return self.year.in_(1)

    @property
    def is_last_year(self) -> bool:
        """Return True if target is in the calendar year immediately before the reference.

        Shortcut: equivalent to calling self.in_years(-1).
        """
        return self.year.in_(-1)

    # Compact cached namespaces (short 2-4 char names). These are lazy
    # properties that construct a small namespace object delegating to the
    # existing `in_*` methods. They are non-invasive and do not change
    # the canonical API surface which remains the `in_*` methods.

    @cached_property
    def minute(self) -> MinuteNamespace:
        return MinuteNamespace(self)

    @cached_property
    def hour(self) -> HourNamespace:
        return HourNamespace(self)

    @cached_property
    def day(self) -> DayNamespace:
        return DayNamespace(self)

    @cached_property
    def week(self) -> WeekNamespace:
        return WeekNamespace(self)

    @cached_property
    def month(self) -> MonthNamespace:
        return MonthNamespace(self)

    @cached_property
    def qtr(self) -> QuarterNamespace:
        return QuarterNamespace(self)

    @cached_property
    def year(self) -> YearNamespace:
        return YearNamespace(self)