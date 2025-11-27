"""
Business logic object for frist.

Provides policy-aware business calendar calculations (working days, business days,
and range membership helpers). This module is intentionally independent from Age
and Cal; Chrono composes Biz when policy-aware operations are required.
"""
import datetime as dt
from typing import Callable
from functools import cached_property

from ._biz_policy import BizPolicy
from ._util import verify_start_end, in_half_open,in_half_open_date
from ._ranges import UnitNamespace

class Biz:
    """Policy-aware business calendar utilities.

    Biz wraps a pair of datetimes (`target_time` and `ref_time`) together with a
    `BizPolicy` to provide business-oriented calculations such as
    fractional `business_days` and `working_days`, range membership helpers
    (in_business_days, in_working_days) and fiscal helpers.

    The class is intentionally small and focused: it performs policy-aware
    operations and leaves policy-free calendar/time calculations to `Cal`.
    """
    def __init__(self, target_time: dt.datetime, ref_time: dt.datetime | None=None, policy: BizPolicy | None=None) -> None:
        """Initialize a `Biz` instance.

        Args:
            target_time: The datetime being inspected or measured from.
            ref_time: The reference datetime (defaults to now when omitted).
            policy: Optional `BizPolicy`. If omitted, a default policy is used.
        """
        self.cal_policy: BizPolicy = policy or BizPolicy()
        self.target_time: dt.datetime = target_time
        self.ref_time: dt.datetime = ref_time or dt.datetime.now()

    def __repr__(self) -> str:
        """Return a concise representation useful for debugging."""
        return f"<Biz target_time={self.target_time!r} ref_time={self.ref_time!r} policy={self.cal_policy!r}>"

    # ---------- Properties ----------
    @property
    def holiday(self) -> bool:
        """Return True if `target_time` falls on a holiday defined by the policy."""
        return self.cal_policy.is_holiday(self.target_time)

    @property
    def is_workday(self) -> bool:
        """Return True if `target_time` is a workday according to the policy."""
        return self.cal_policy.is_workday(self.target_time)

    @property
    def is_business_day(self) -> bool:
        """Return True if `target_time` is a business day (workday and not holiday)."""
        return self.cal_policy.is_business_day(self.target_time)

    # ---------- Shortcut properties (policy-aware) ----------
    @property
    def is_business_last_day(self) -> bool:
        """Shortcut: True when the target is in the business-day immediately before the reference.

        Equivalent to calling `in_business_days(-1)`.
        """
        return self.in_business_days(-1)

    @property
    def is_business_this_day(self) -> bool:
        """Shortcut: True when the target is in the business-day of the reference.

        Equivalent to calling `in_business_days(0)`.
        """
        return self.in_business_days(0)

    @property
    def is_business_next_day(self) -> bool:
        """Shortcut: True when the target is in the business-day immediately after the reference.

        Equivalent to calling `in_business_days(1)`.
        """
        return self.in_business_days(1)

    @property
    def is_workday_last_day(self) -> bool:
        """Shortcut: True when the target is in the workday immediately before the reference.

        Equivalent to calling `in_working_days(-1)`.
        """
        return self.in_working_days(-1)

    @property
    def is_workday_this_day(self) -> bool:
        """Shortcut: True when the target is in the workday of the reference.

        Equivalent to calling `in_working_days(0)`.
        """
        return self.in_working_days(0)

    @property
    def is_workday_next_day(self) -> bool:
        """Shortcut: True when the target is in the workday immediately after the reference.

        Equivalent to calling `in_working_days(1)`.
        """
        return self.in_working_days(1)

    # Fiscal shortcuts (explicitly fiscal-aware)
    @property
    def is_last_fiscal_quarter(self) -> bool:
        """Shortcut: True when the target is in the fiscal quarter immediately before the reference.

        Equivalent to calling `in_fiscal_quarters(-1)`.
        """
        return self.in_fiscal_quarters(-1)

    @property
    def is_this_fiscal_quarter(self) -> bool:
        """Shortcut: True when the target is in the same fiscal quarter as the reference.

        Equivalent to calling `in_fiscal_quarters(0)`.
        """
        return self.in_fiscal_quarters(0)

    @property
    def is_next_fiscal_quarter(self) -> bool:
        """Shortcut: True when the target is in the fiscal quarter immediately after the reference.

        Equivalent to calling `in_fiscal_quarters(1)`.
        """
        return self.in_fiscal_quarters(1)

    @property
    def is_last_fiscal_year(self) -> bool:
        """Shortcut: True when the target is in the fiscal year immediately before the reference.

        Equivalent to calling `in_fiscal_years(-1)`.
        """
        return self.in_fiscal_years(-1)

    @property
    def is_this_fiscal_year(self) -> bool:
        """Shortcut: True when the target is in the same fiscal year as the reference.

        Equivalent to calling `in_fiscal_years(0)`.
        """
        return self.in_fiscal_years(0)

    @property
    def is_next_fiscal_year(self) -> bool:
        """Shortcut: True when the target is in the fiscal year immediately after the reference.

        Equivalent to calling `in_fiscal_years(1)`.
        """
        return self.in_fiscal_years(1)

    # Alias for external convenience
    #@property
    #def business_day_fraction(self) -> float:
    #    return self.business_days()

    @property
    def fiscal_year(self) -> int:
        return self.get_fiscal_year(self.target_time, self.cal_policy.fiscal_year_start_month)
    
    @property
    def fiscal_quarter(self) -> int:
        return self.get_fiscal_quarter(self.target_time, self.cal_policy.fiscal_year_start_month)


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
        cur: float = (dt.datetime.combine(dt_obj.date(), dt_obj.time()) - start_dt).total_seconds()
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
        """Generic day-iterator that sums fractional contributions for days where check_fn(day_dt) is True.

        `check_fn` receives a datetime on the day being considered. `frac_fn`, if
        provided, is used to compute the fractional business-day progress for a
        given datetime; otherwise the policy's `business_day_fraction` is used
        (which returns 0.0 for holidays).
        """
        if self.target_time > self.ref_time:
            raise ValueError(f"{self.target_time=} must not be after {self.ref_time=}")

        if frac_fn is None:
            frac_fn = self.cal_policy.business_day_fraction

        current: dt.datetime = self.target_time
        end: dt.datetime = self.ref_time
        total: float = 0.0

        while current.date() <= end.date():
            if check_fn(current):
                # Determine window for this day
                if current.date() == self.target_time.date():
                    start_dt: dt.datetime = self.target_time
                    end_dt: dt.datetime = min(end, dt.datetime.combine(current.date(), self.cal_policy.end_of_business))
                elif current.date() == end.date():
                    start_dt = dt.datetime.combine(current.date(), self.cal_policy.start_of_business)
                    end_dt = end
                else:
                    start_dt = dt.datetime.combine(current.date(), self.cal_policy.start_of_business)
                    end_dt = dt.datetime.combine(current.date(), self.cal_policy.end_of_business)

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
    def _move_n_days(self, start_date: dt.date, n: int, count_business: bool) -> dt.date:
        """Move `n` business/working days from start_date, skipping days that don't count.

        If n is positive, moves forward; if negative, moves backward. Returns the date reached after moving.
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
        """Return True if target_time.date() is within the business-day range [start, end] counted from ref_time.date().

        Both start and end are integers (can be negative). The window is computed by moving start and end business-days from ref_date.
        The target must itself be a business day to be considered "in" the business-day window.
        """
        
        ref: dt.date = self.ref_time.date()
        tgt: dt.date = self.target_time.date()
        start_date: dt.date = self._move_n_days(ref, start, count_business=True)
        end_date: dt.date = self._move_n_days(ref, end, count_business=True)

        lower, upper = start_date, end_date

        # target must be a business day
        if not self.cal_policy.is_business_day(tgt):
            return False

        # Half-open semantics: start is inclusive, end is exclusive.
        return in_half_open_date(lower, tgt, upper)

    @verify_start_end
    def in_working_days(self, start: int = 0, end: int = 0) -> bool:
        """Return True if target_time.date() is within the working-day range [start, end] counted from ref_time.date().

        Working days ignore holidays (only policy.workdays matter).
        """
        
        ref: dt.date = self.ref_time.date()
        tgt: dt.date = self.target_time.date()
        start_date: dt.date = self._move_n_days(ref, start, count_business=False)
        end_date: dt.date = self._move_n_days(ref, end, count_business=False)

        lower, upper = start_date, end_date

        if not self.cal_policy.is_workday(tgt):
            return False

        # Half-open semantics: include `lower`, exclude `upper`.
        return in_half_open_date(lower, tgt, upper)

    @verify_start_end
    def in_fiscal_quarters(self, start: int = 0, end: int = 0) -> bool:
        """
        True if timestamp falls within the fiscal quarter window(s) from start to end.

        Uses a half-open interval: start_tuple <= target_tuple < (end_tuple[0], end_tuple[1] + 1).

        Args:
            start: Fiscal quarters from now to start range (negative = past, 0 = this fiscal quarter, positive = future)
            end: Fiscal quarters from now to end range (defaults to start for single fiscal quarter)

        Examples:
            chrono.cal.in_fiscal_quarters(0)          # This fiscal quarter
            chrono.cal.in_fiscal_quarters(-1)         # Last fiscal quarter
            chrono.cal.in_fiscal_quarters(-4, -1)     # From 4 fiscal quarters ago through last fiscal quarter
            chrono.cal.in_fiscal_quarters(-8, 0)      # Last 8 fiscal quarters through this fiscal quarter
        """
        
        fy_start_month: int = self.cal_policy.fiscal_year_start_month
        base_time: dt.datetime = self.ref_time
        fy: int = Biz.get_fiscal_year(base_time, fy_start_month)
        fq: int = Biz.get_fiscal_quarter(base_time, fy_start_month)

        # Use a monotonic fiscal-quarter index (fy * 4 + (fq-1)) so we can
        # compare fiscal quarters with integer arithmetic (consistent with
        # `_month_index` and the `Cal.in_quarters` implementation).
        base_idx = fy * 4 + (fq - 1)

        def fiscal_quarter_index_for_offset(offset: int) -> int:
            return base_idx + offset

        start_idx = fiscal_quarter_index_for_offset(start)
        end_idx = fiscal_quarter_index_for_offset(end)

        target_fy: int = Biz.get_fiscal_year(self.target_time, fy_start_month)
        target_fq: int = Biz.get_fiscal_quarter(self.target_time, fy_start_month)
        target_idx = target_fy * 4 + (target_fq - 1)

        # Use in_half_open on integer quarter indices. The decorator
        # normalization already makes single-arg calls represent a single-quarter
        # half-open window, so `end_idx` is the exclusive end.
        return in_half_open(start_idx, target_idx, end_idx)

    @verify_start_end
    def in_fiscal_years(self, start: int = 0, end: int = 0) -> bool:
        """
        True if timestamp falls within the fiscal year window(s) from start to end.

        Uses a half-open interval: start_year <= target_year < end_year + 1.

        Args:
            start: Fiscal years from now to start range (negative = past, 0 = this fiscal year, positive = future)
            end: Fiscal years from now to end range (defaults to start for single fiscal year)

        Examples:
            chrono.cal.in_fiscal_years(0)          # This fiscal year
            chrono.cal.in_fiscal_years(-1)         # Last fiscal year
            chrono.cal.in_fiscal_years(-5, -1)     # From 5 fiscal years ago through last fiscal year
            chrono.cal.in_fiscal_years(-10, 0)     # Last 10 fiscal years through this fiscal year
        """
        
        fy_start_month: int = self.cal_policy.fiscal_year_start_month
        base_time: dt.datetime = self.ref_time
        fy: int = Biz.get_fiscal_year(base_time, fy_start_month)
        start_year: int = fy + start
        end_year: int = fy + end

        target_fy: int = Biz.get_fiscal_year(self.target_time, fy_start_month)

        # Use in_half_open for numeric years; the decorator normalization
        # already makes single-arg calls represent a single-year half-open
        # interval, so `end_year` is the exclusive end.
        return in_half_open(start_year, target_fy, end_year)

    # (Removed duplicate private `_in_*_impl` helper functions; the public
    # decorated `in_*` methods above are the single canonical implementation.)
    
    @staticmethod
    def get_fiscal_year(dt: dt.datetime, fy_start_month: int) -> int:
        """Return the fiscal year for a given datetime and fiscal year start month."""
        return dt.year if dt.month >= fy_start_month else dt.year - 1

    @staticmethod
    def get_fiscal_quarter(dt: dt.datetime, fy_start_month: int) -> int:
        """Return the fiscal quarter for a given datetime and fiscal year start month."""
        offset: int = (dt.month - fy_start_month) % 12 if dt.month >= fy_start_month else (dt.month + 12 - fy_start_month) % 12
        return (offset // 3) + 1

    # Compact cached namespaces for policy-aware ranges. These provide a
    # compact ergonomic surface that delegates to the public decorated `in_*`
    # methods (e.g., `in_business_days`, `in_working_days`). The public
    # `in_*` methods are the canonical implementations; `UnitNamespace` is
    # an ergonomic, non-invasive adapter that forwards to them.

    @cached_property
    def bday(self) -> UnitNamespace:
        return UnitNamespace(self, self.in_business_days)

    @cached_property
    def wday(self) -> UnitNamespace:
        return UnitNamespace(self, self.in_working_days)

    @cached_property
    def fqtr(self) -> UnitNamespace:
        return UnitNamespace(self, self.in_fiscal_quarters)

    @cached_property
    def fyr(self) -> UnitNamespace:
        return UnitNamespace(self, self.in_fiscal_years)


__all__ = ["Biz"]
