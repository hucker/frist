"""
Business logic object for frist.

Provides policy-aware business calendar calculations (working days, business days,
and range membership helpers). This module is intentionally independent from Age
and Cal; Chrono composes Biz when policy-aware operations are required.
"""

import datetime as dt
from collections.abc import Callable
from functools import cached_property

from ._biz_policy import BizPolicy
from ._types import TimeLike, time_pair
from ._util import in_half_open, in_half_open_date, verify_start_end
from .units import (
    BizDayUnit,
    FiscalQuarterUnit,
    FiscalYearUnit,
    WorkingDayUnit,
)


class Biz:
    """Policy-aware business calendar utilities.

    Biz wraps a pair of datetimes (`target_time` and `ref_time`) together with a
    `BizPolicy` to provide business-oriented calculations such as
    fractional `business_days` and `working_days`, range membership helpers
    (in_business_days, in_working_days) and fiscal helpers.

    The class is intentionally small and focused: it performs policy-aware
    operations and leaves policy-free calendar/time calculations to `Cal`.
    """

    def __init__(
        self,
        target_dt: TimeLike,
        ref_dt: TimeLike | None = None,
        policy: BizPolicy | None = None,
        formats: list[str] | None = None,
    ) -> None:
        """Initialize a `Biz` instance.

        Args:
            target_time: The datetime being inspected or measured from.
                         Can be dt.datetime, dt.date, float, int, or str.
            ref_time: The reference datetime (defaults to now when omitted).
                      Can be dt.datetime, dt.date, float, int, str, or None.
            policy: Optional `BizPolicy`. If omitted, a default policy is used.
            formats: Optional list of datetime formats for string parsing.
        """
        self.cal_policy: BizPolicy = policy or BizPolicy()

        # Normalize and validate timezone compatibility via centralized utility
        if ref_dt is None:
            ref_dt = dt.datetime.now()
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

    def __repr__(self) -> str:
        """Return a concise representation useful for debugging."""
        return f"<Biz {self.target_dt=!r} {self.ref_dt=!r} {self.cal_policy=!r}>"

    # ---------- Properties ----------
    @property
    def holiday(self) -> bool:
        """Return True if `target_time` falls on a holiday defined by the policy."""
        return self.cal_policy.is_holiday(self.target_dt)

    @property
    def is_workday(self) -> bool:
        """Return True if `target_time` is a workday according to the policy."""
        return self.cal_policy.is_workday(self.target_dt)

    @property
    def is_business_day(self) -> bool:
        """Return True if `target_time` is a business day (workday and not holiday)."""
        return self.cal_policy.is_business_day(self.target_dt)

    # ---------- Shortcut properties (policy-aware) ----------
    @property
    def is_business_last_day(self) -> bool:
        """Shortcut: True when target is in the business-day immediately before ref_dt.
        """
        return self.biz_day.in_(-1)

    @property
    def is_business_this_day(self) -> bool:
        """Shortcut: True when the target is in the business-day of the ref_dt.
        """
        return self.biz_day.in_(0)

    @property
    def is_business_next_day(self) -> bool:
        """Shortcut: True when target is in the business-day immediately after ref_dt
        """
        return self.biz_day.in_(1)

    @property
    def is_workday_last_day(self) -> bool:
        """Shortcut: True when target is in the workday immediately before the ref_dt
        """
        return self.work_day.in_(-1)

    @property
    def is_workday_this_day(self) -> bool:
        """Shortcut: True when target is in the workday of the reference.
        """
        return self.work_day.in_(0)

    @property
    def is_workday_next_day(self) -> bool:
        """Shortcut: True when target is in the workday immediately after the ref_dt
        """
        return self.work_day.in_(1)

    # Fiscal shortcuts (explicitly fiscal-aware)
    @property
    def is_last_fiscal_quarter(self) -> bool:
        """Shortcut: True when target is in the fiscal quarter immediately before ref_dt
        """
        return self.fis_qtr.in_(-1)

    @property
    def is_this_fiscal_quarter(self) -> bool:
        """Shortcut: True when the target is in the same fiscal quarter as the ref_dt
        """
        return self.fis_qtr.in_(0)

    @property
    def is_next_fiscal_quarter(self) -> bool:
        """Shortcut: True when target is in the fiscal quarter immediately after ref_dt.
        """
        return self.fis_qtr.in_(1)

    @property
    def is_last_fiscal_year(self) -> bool:
        """Shortcut: True when target is in the fiscal year immediately before ref_dt.
        """
        return self.fis_year.in_(-1)

    @property
    def is_this_fiscal_year(self) -> bool:
        """Shortcut: True when the target is in the same fiscal year as the reference.
        """
        return self.fis_year.in_(0)

    @property
    def is_next_fiscal_year(self) -> bool:
        """Shortcut: True when target is in the fiscal year immediately after ref_dt.

        """
        return self.fis_year.in_(1)

    # Alias for external convenience
    # @property
    # def business_day_fraction(self) -> float:
    #    return self.business_days()

    @property
    def fiscal_year(self) -> int:
        return self.fis_year.val

    @property
    def fiscal_quarter(self) -> int:
        return self.fis_qtr.val

    def _workday_fraction_at(self, dt_obj: dt.datetime) -> float:
        """Fraction of business-day elapsed at dt_obj, ignoring holidays/workday checks.

        Computes fraction between policy.start_of_business and policy.end_of_business
        for the given date using the time component of dt_obj.
        """
        start: dt.time = self.cal_policy.start_of_business
        end: dt.time = self.cal_policy.end_of_business
        start_dt: dt.datetime = dt.datetime.combine(dt_obj.date(), start)
        end_dt: dt.datetime = dt.datetime.combine(dt_obj.date(), end)
        total: float = (end_dt - start_dt).total_seconds()
        cur: float = (
            dt.datetime.combine(dt_obj.date(), dt_obj.time()) - start_dt
        ).total_seconds()
        if cur <= 0:
            return 0.0
        if cur >= total:
            return 1.0
        return cur / total if total > 0 else 0.0

    def _age_days_helper(
        self,
        check_fn: Callable[[dt.datetime], bool],
        frac_fn: Callable[[dt.datetime], float] | None = None,
    ) -> float:
        """Generic day-iterator that sums fractional contributions for days 
           where check_fn(day_dt) is True.

        `check_fn` receives a datetime on the day being considered. `frac_fn`, if
        provided, is used to compute the fractional business-day progress for a
        given datetime; otherwise the policy's `business_day_fraction` is used
        (which returns 0.0 for holidays).
        """
        if self.target_dt > self.ref_dt:
            raise ValueError(f"{self.target_dt=} must not be after {self.ref_dt=}")

        if frac_fn is None:
            frac_fn = self.cal_policy.business_day_fraction

        current: dt.datetime = self.target_dt
        end: dt.datetime = self.ref_dt
        total: float = 0.0

        while current.date() <= end.date():
            if check_fn(current):
                # Determine window for this day
                if current.date() == self.target_dt.date():
                    start_dt: dt.datetime = self.target_dt
                    end_dt: dt.datetime = min(
                        end,
                        dt.datetime.combine(
                            current.date(), self.cal_policy.end_of_business
                        ),
                    )
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(
                        current.date(), self.cal_policy.start_of_business
                    )
                    end_dt = end
                else:
                    start_dt = dt.datetime.combine(
                        current.date(), self.cal_policy.start_of_business
                    )
                    end_dt = dt.datetime.combine(
                        current.date(), self.cal_policy.end_of_business
                    )

                frac: float = frac_fn(end_dt) - frac_fn(start_dt)
                total += max(frac, 0.0)
            current = current + dt.timedelta(days=1)

        return total

    # ---------- Public calculations ----------
    @property
    def business_days(self) -> float:
        """Fractional business days between target_time and ref_time.

        Business day = policy.is_workday(date) AND not policy.is_holiday(date).
        """

        def check(dt_obj: dt.datetime) -> bool:
            return self.cal_policy.is_business_day(dt_obj)

        return self._age_days_helper(check)

    @property
    def working_days(self) -> float:
        """Fractional working days between target_time and ref_time.

        Working days are defined by policy.is_workday (ignores holidays) and are
        counted fractionally using business hours.
        """

        def check(dt_obj: dt.datetime) -> bool:
            return self.cal_policy.is_workday(dt_obj)

        return self._age_days_helper(check, self._workday_fraction_at)

    # ---------- Range membership helpers ----------
    def _move_n_days(
        self, start_date: dt.date, n: int, count_business: bool
    ) -> dt.date:
        """Move n business/working days from start_date, skipping days that don't count

        If n is positive, moves forward; if negative, moves backward. Returns the 
        date reached after moving.
        """
        if n == 0:
            return start_date

        step: int = 1 if n > 0 else -1
        remaining: int = abs(n)
        current: dt.date = start_date

        while remaining > 0:
            current = current + dt.timedelta(days=step)
            # Determine if the current day counts
            if count_business:
                counts: bool = self.cal_policy.is_business_day(current)
            else:
                counts = self.cal_policy.is_workday(current)
            if counts:
                remaining -= 1

        return current

    @verify_start_end
    def in_business_days(self, start: int = 0, end: int = 0) -> bool:
        """True if `target_dt.date()` is within the business-day window [start, end)."""
        return self.biz_day.in_(start, end)

    @verify_start_end
    def in_working_days(self, start: int = 0, end: int = 0) -> bool:
        """True if `target_dt.date()` is within the working-day window [start, end)."""
        return self.work_day.in_(start, end)

    @verify_start_end
    def in_fiscal_quarters(self, start: int = 0, end: int = 0) -> bool:
        """True if timestamp falls within the fiscal quarter window(s)."""
        return self.fis_qtr.in_(start, end)

    @verify_start_end
    def in_fiscal_years(self, start: int = 0, end: int = 0) -> bool:
        """True if timestamp falls within the fiscal year window(s)."""
        return self.fis_year.in_(start, end)

    @staticmethod
    def get_fiscal_year(dt_: dt.datetime, fy_start_month: int) -> int:
        """Return the fiscal year for a given datetime and fiscal year start month."""
        return dt_.year if dt_.month >= fy_start_month else dt_.year - 1

    @staticmethod
    def get_fiscal_quarter(dt_: dt.datetime, fy_start_month: int) -> int:
        """Return the fiscal quarter for a given datetime and fiscal year start month."""
        offset: int = (
            (dt_.month - fy_start_month) % 12
            if dt_.month >= fy_start_month
            else (dt_.month + 12 - fy_start_month) % 12
        )
        return (offset // 3) + 1

    # Compact cached units for policy-aware ranges. These provide a
    # compact ergonomic surface that delegates to the public decorated `in_*`
    # methods (e.g., `in_business_days`, `in_working_days`). The public
    # `in_*` methods are the canonical implementations; `Unit` is
    # an ergonomic, non-invasive adapter that forwards to them.

    @cached_property
    def biz_day(self) -> BizDayUnit:
        """Returns a BizDayUnit for business day range checks and utilities."""
        return BizDayUnit(self, self.cal_policy)

    @cached_property
    def work_day(self) -> WorkingDayUnit:
        """Returns a WorkingDayUnit for working day range checks and utilities."""
        return WorkingDayUnit(self, self.cal_policy)

    @cached_property
    def fis_qtr(self) -> FiscalQuarterUnit:
        """Returns a FiscalQuarterUnit for fiscal quarter range checks and utilities."""
        return FiscalQuarterUnit(self, self.cal_policy)

    @cached_property
    def fis_year(self) -> FiscalYearUnit:
        """Returns a FiscalYearUnit for fiscal year range checks and utilities."""
        return FiscalYearUnit(self, self.cal_policy)


__all__ = ["Biz"]
