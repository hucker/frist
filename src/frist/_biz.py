"""
Business logic object for frist.

Provides policy-aware business calendar calculations (working days, business days,
and range membership helpers). This module is intentionally independent from Age
and Cal; Chrono composes Biz when policy-aware operations are required.
"""

import datetime as dt
from functools import cached_property

from ._biz_policy import BizPolicy
from ._types import TimeLike, time_pair

# No verify_start_end decorators needed; unit adapters are used directly.
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
    def is_business_day_yesterday(self) -> bool:
        """Shortcut: True when target is in the business-day immediately before ref_dt.
        """
        return self.biz_day.in_(-1)

    @property
    def is_business_day_today(self) -> bool:
        """Shortcut: True when the target is in the business-day of the ref_dt.
        """
        return self.biz_day.in_(0)

    @property
    def is_business_day_tomorrow(self) -> bool:
        """Shortcut: True when target is in the business-day immediately after ref_dt
        """
        return self.biz_day.in_(1)

    @property
    def is_workday_yesterday(self) -> bool:
        """Shortcut: True when target is in the workday immediately before the ref_dt
        """
        return self.work_day.in_(-1)

    @property
    def is_workday_today(self) -> bool:
        """Shortcut: True when target is in the workday of the reference.
        """
        return self.work_day.in_(0)

    @property
    def is_workday_tomorrow(self) -> bool:
        """Shortcut: True when target is in the workday immediately after the ref_dt
        """
        return self.work_day.in_(1)

    # No backward-compatible aliases; tests and API use explicit
    # today/yesterday/tomorrow names.

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
    
    
    # ---------- Public calculations ----------
    @property
    def business_days(self) -> float:
        """Fractional business days between target_time and ref_time using half-open interval.

        Delegates to `biz_day.business_days()`.
        """
        return self.biz_day.business_days()

    @property
    def working_days(self) -> float:
        """Fractional working days between target_time and ref_time using half-open interval.

        Delegates to `work_day.working_days()`.
        """
        return self.work_day.working_days()

    # (No in_* forwards; use unit adapters directly.)

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
