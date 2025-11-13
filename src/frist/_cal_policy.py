import datetime as dt
from dataclasses import dataclass, field
from typing import List, Set

"""
Business calendar policy for fiscal years, workdays, business hours, and holidays.
"""

@dataclass
class CalendarPolicy:

    fiscal_year_start_month: int = 1
    workdays: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Monday=0 ... Friday=4
    start_of_business: dt.time = dt.time(9, 0)
    end_of_business: dt.time = dt.time(17, 0)
    holidays: Set[str] = field(default_factory=set)
    

    def is_weekend(self, value: int | dt.date | dt.datetime) -> bool:
        """
        Return True if the given date or datetime is not a workday.
        Accepts datetime.date, datetime.datetime, or weekday int.
        """
        if isinstance(value, int):
            weekday = value
        elif hasattr(value, 'weekday'):
            weekday = value.weekday()
        else:
            raise TypeError("is_weekend expects int, date, or datetime")
        return not self.is_workday(weekday)


    def is_workday(self, value: int | dt.date | dt.datetime) -> bool:
        """
        Return True if the given date or datetime is a workday according to policy.
        Accepts datetime.date, datetime.datetime, or weekday int.
        """
        if isinstance(value, int):
            weekday = value
        elif hasattr(value, 'weekday'):
            weekday = value.weekday()
        else:
            raise TypeError("is_workday expects int, date, or datetime")
        return weekday in self.workdays

    def is_business_time(self, time: dt.time) -> bool:
        """
        Return True if the given time is within business hours.
        Uses strict datetime.time for start and end.
        """
        return self.start_of_business <= time < self.end_of_business

    def is_holiday(self, date_str: str) -> bool:
        """
        Return True if the date string (YYYY-MM-DD) is a holiday according to policy.
        """
        return date_str in self.holidays
    
    def business_day_fraction(self, dt_obj: dt.datetime) -> float:
        """
        Return the fraction of the business day completed at the given datetime.

        - Returns 0.0 for holidays, weekends, or times at/before start_of_business.
        - Returns 1.0 for times at/after end_of_business.
        - Returns a linear fraction for times in between.

        Args:
            dt_obj: datetime to evaluate

        Returns:
            float: Fraction of business day completed (0.0 to 1.0)
        """
        weekday = dt_obj.weekday()
        date_str = dt_obj.strftime('%Y-%m-%d')
        if self.is_holiday(date_str) or not self.is_workday(weekday):
            return 0.0
        start = self.start_of_business
        end = self.end_of_business
        time = dt_obj.time()
        total_seconds = (end.hour - start.hour) * 3600 + (end.minute - start.minute) * 60 + (end.second - start.second)
        current_seconds = (time.hour - start.hour) * 3600 + (time.minute - start.minute) * 60 + (time.second - start.second)
        if current_seconds <= 0:
            return 0.0
        if current_seconds >= total_seconds:
            return 1.0
        return current_seconds / total_seconds if total_seconds > 0 else 0.0
