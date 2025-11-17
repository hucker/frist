"""
Tests for fiscal year and fiscal quarter properties in Chrono and Cal.
"""

import datetime as dt

from frist import Chrono,CalendarPolicy


def test_fiscal_year_and_quarter_january_start():
    """Fiscal year and quarter with January start (default)."""
    target_time = dt.datetime(2024, 2, 15)  # February 2024
    cal = Chrono(target_time=target_time).cal
    assert cal.fiscal_year == 2024, "Fiscal year should be 2024 for Feb 2024 with January start"
    assert cal.fiscal_quarter == 1, "Fiscal quarter should be 1 (Jan-Mar) for Feb 2024 with January start"

    target_time = dt.datetime(2024, 4, 1)  # April 2024
    cal = Chrono(target_time=target_time).cal
    assert cal.fiscal_quarter == 2, "Fiscal quarter should be 2 (Apr-Jun) for April 2024 with January start"


def test_fiscal_year_and_quarter_april_start():
    """Fiscal year and quarter with April start."""
    
    policy: CalendarPolicy = CalendarPolicy(fiscal_year_start_month=4)

    target_time = dt.datetime(2024, 3, 31)  # March 2024
    cal = Chrono(target_time=target_time, policy=policy).cal
    assert cal.fiscal_year == 2023, "Fiscal year should be 2023 for Mar 2024 with April start"
    assert cal.fiscal_quarter == 4, "Fiscal quarter should be 4 (Jan-Mar) for Mar 2024 with April start"

    target_time = dt.datetime(2024, 4, 1)  # April 2024
    cal = Chrono(target_time=target_time, policy=policy).cal
    assert cal.fiscal_year == 2024, "Fiscal year should be 2024 for Apr 2024 with April start"
    assert cal.fiscal_quarter == 1, "Fiscal quarter should be 1 (Apr-Jun) for Apr 2024 with April start"

    target_time = dt.datetime(2024, 7, 15)  # July 2024
    cal = Chrono(target_time=target_time, policy=policy).cal
    assert cal.fiscal_quarter == 2, "Fiscal quarter should be 2 (Jul-Sep) for Jul 2024 with April start"

    target_time = dt.datetime(2024, 10, 1)  # October 2024
    cal = Chrono(target_time=target_time,policy=policy).cal
    assert cal.fiscal_quarter == 3, "Fiscal quarter should be 3 (Oct-Dec) for Oct 2024 with April start"

    target_time = dt.datetime(2025, 1, 1)  # January 2025
    cal = Chrono(target_time=target_time,policy=policy).cal
    assert cal.fiscal_quarter == 4, "Fiscal quarter should be 4 (Jan-Mar) for Jan 2025 with April start"
