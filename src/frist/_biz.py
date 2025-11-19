"""
Business logic object for frist.

Provides policy-aware business calendar calculations (working days, business days,
and range membership helpers). This module is intentionally independent from Age
and Cal; Chrono composes Biz when policy-aware operations are required.
"""
import datetime as dt
from typing import Callable

from ._cal_policy import CalendarPolicy


class Biz:
    def __init__(self, target_time: dt.datetime, ref_time: dt.datetime | None, policy: CalendarPolicy | None) -> None:
        self.cal_policy: CalendarPolicy = policy or CalendarPolicy()
        self.target_time: dt.datetime = target_time
        self.ref_time: dt.datetime = ref_time or dt.datetime.now()

    def __repr__(self) -> str:
        return f"<Biz target_time={self.target_time!r} ref_time={self.ref_time!r} policy={self.cal_policy!r}>"

    # ---------- Properties ----------
    @property
    def holiday(self) -> bool:
        return self.cal_policy.is_holiday(self.target_time)

    @property
    def is_workday(self) -> bool:
        return self.cal_policy.is_workday(self.target_time)

    @property
    def is_business_day(self) -> bool:
        return self.cal_policy.is_business_day(self.target_time)

    # Alias for external convenience
    @property
    def business_day_fraction(self) -> float:
        return self.business_days()

    # ---------- Internal helpers ----------
    def _workday_fraction_at(self, dt_obj: dt.datetime) -> float:
        """Fraction of business-day elapsed at dt_obj, ignoring holidays/workday checks.

        This computes fraction between policy.start_of_business and policy.end_of_business
        for the given date using the time component of dt_obj.
        """
        start = self.cal_policy.start_of_business
        end = self.cal_policy.end_of_business
        start_dt = dt.datetime.combine(dt_obj.date(), start)
        end_dt = dt.datetime.combine(dt_obj.date(), end)
        total = (end_dt - start_dt).total_seconds()
        cur = (dt.datetime.combine(dt_obj.date(), dt_obj.time()) - start_dt).total_seconds()
        if cur <= 0:
            return 0.0
        if cur >= total:
            return 1.0
        return cur / total if total > 0 else 0.0

    def _age_days_helper(self, check_fn: Callable[[dt.datetime], bool]) -> float:
        """Generic day-iterator that sums fractional contributions for days where check_fn(day_dt) is True.

        check_fn receives a datetime on the day being considered (time portion will be respected by business_day_fraction).
        """
        if self.target_time > self.ref_time:
            raise ValueError("target_time must not be after ref_time")

        current = self.target_time
        end = self.ref_time
        total = 0.0

        while current.date() <= end.date():
            if check_fn(current):
                # Determine window for this day
                if current.date() == self.target_time.date():
                    start_dt = self.target_time
                    end_dt = min(end, dt.datetime.combine(current.date(), self.cal_policy.end_of_business))
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(current.date(), self.cal_policy.start_of_business)
                    end_dt = end
                else:
                    start_dt = dt.datetime.combine(current.date(), self.cal_policy.start_of_business)
                    end_dt = dt.datetime.combine(current.date(), self.cal_policy.end_of_business)

                frac = self.cal_policy.business_day_fraction(end_dt) - self.cal_policy.business_day_fraction(start_dt)
                total += max(frac, 0.0)
            current += dt.timedelta(days=1)

        return total

    # ---------- Public calculations ----------
    def business_days(self) -> float:
        """Fractional business days between target_time and ref_time.

        Business day = policy.is_workday(date) AND not policy.is_holiday(date).
        """
        def check(dt_obj: dt.datetime) -> bool:
            return self.cal_policy.is_business_day(dt_obj)

        return self._age_days_helper(check)

    def working_days(self) -> float:
        """Fractional working days between target_time and ref_time.

        Working days are defined by policy.is_workday (ignores holidays) and are
        counted fractionally using business hours.
        """
        if self.target_time > self.ref_time:
            raise ValueError("target_time must not be after ref_time")

        current = self.target_time
        end = self.ref_time
        total = 0.0

        while current.date() <= end.date():
            if self.cal_policy.is_workday(current):
                # First day
                if current.date() == self.target_time.date():
                    s = self.target_time
                    e = min(end, dt.datetime.combine(current.date(), self.cal_policy.end_of_business))
                # Last day
                elif current.date() == end.date():
                    s = dt.datetime.combine(current.date(), self.cal_policy.start_of_business)
                    e = end
                else:
                    s = dt.datetime.combine(current.date(), self.cal_policy.start_of_business)
                    e = dt.datetime.combine(current.date(), self.cal_policy.end_of_business)

                frac = self._workday_fraction_at(e) - self._workday_fraction_at(s)
                total += max(frac, 0.0)
            current += dt.timedelta(days=1)

        return total

    # ---------- Range membership helpers ----------
    def _move_n_days(self, start_date: dt.date, n: int, count_business: bool) -> dt.date:
        """Move `n` business/working days from start_date, skipping days that don't count.

        If n is positive, moves forward; if negative, moves backward. Returns the date reached after moving.
        """
        if n == 0:
            return start_date

        step = 1 if n > 0 else -1
        remaining = abs(n)
        current = start_date

        while remaining > 0:
            current = current + dt.timedelta(days=step)
            # Determine if the current day counts
            if count_business:
                counts = self.cal_policy.is_business_day(current)
            else:
                counts = self.cal_policy.is_workday(current)
            if counts:
                remaining -= 1

        return current

    def in_business_days(self, start: int = 0, end: int = 0) -> bool:
        """Return True if target_time.date() is within the business-day range [start, end] counted from ref_time.date().

        Both start and end are integers (can be negative). The window is computed by moving start and end business-days from ref_date.
        The target must itself be a business day to be considered "in" the business-day window.
        """
        ref = self.ref_time.date()
        tgt = self.target_time.date()
        start_date = self._move_n_days(ref, start, count_business=True)
        end_date = self._move_n_days(ref, end, count_business=True)

        # Normalize ordering
        if start_date <= end_date:
            lower, upper = start_date, end_date
        else:
            lower, upper = end_date, start_date

        # target must be a business day
        if not self.cal_policy.is_business_day(tgt):
            return False

        return lower <= tgt <= upper

    def in_working_days(self, start: int = 0, end: int = 0) -> bool:
        """Return True if target_time.date() is within the working-day range [start, end] counted from ref_time.date().

        Working days ignore holidays (only policy.workdays matter).
        """
        ref = self.ref_time.date()
        tgt = self.target_time.date()
        start_date = self._move_n_days(ref, start, count_business=False)
        end_date = self._move_n_days(ref, end, count_business=False)

        if start_date <= end_date:
            lower, upper = start_date, end_date
        else:
            lower, upper = end_date, start_date

        if not self.cal_policy.is_workday(tgt):
            return False

        return lower <= tgt <= upper


__all__ = ["Biz"]
