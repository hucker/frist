
"""
Calendar-based time window filtering for frist package.

Provides calendar window filtering functionality for Chrono objects).
"""

import datetime as dt
from functools import cached_property
from typing import TYPE_CHECKING

from ._types import TimeLike, time_pair
from .units import (
    DayUnit,
    HourUnit,
    MinuteUnit,
    MonthUnit,
    QuarterUnit,
    WeekUnit,
    YearUnit,
)

if TYPE_CHECKING:  # pragma: no cover
    pass


class Cal:
    """Calendar window filtering functionality for direct datetime/timestamp inputs."""

    def __init__(
        self,
        target_dt: TimeLike,
        ref_dt: TimeLike,
        formats: list[str] | None = None,
    ) -> None:
        # Normalize and validate timezone compatibility via centralized utility
        self._target_dt, self._ref_dt = time_pair(
            start_time=target_dt,
            end_time=ref_dt,
            formats__=formats,
        )


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

    # Cached units lazily created

    @cached_property
    def minute(self) -> MinuteUnit:
        return MinuteUnit(self)

    @cached_property
    def hour(self) -> HourUnit:
        return HourUnit(self)

    @cached_property
    def day(self) -> DayUnit:
        return DayUnit(self)

    @cached_property
    def week(self) -> WeekUnit:
        return WeekUnit(self)

    @cached_property
    def month(self) -> MonthUnit:
        return MonthUnit(self)

    @cached_property
    def qtr(self) -> QuarterUnit:
        return QuarterUnit(self)

    @cached_property
    def year(self) -> YearUnit:
        return YearUnit(self)