"""
Tests for fiscal year and fiscal quarter properties in Zeit and Cal.
"""
import datetime as dt

from frist import Frist


def test_fiscal_year_and_quarter_january_start():
    """Fiscal year and quarter with January start (default)."""
    target_time = dt.datetime(2024, 2, 15)  # February 2024
    cal = Frist(target_time=target_time).cal
    assert cal.fiscal_year == 2024
    assert cal.fiscal_quarter == 1  # Jan-Mar

    target_time = dt.datetime(2024, 4, 1)  # April 2024
    cal = Frist(target_time=target_time).cal
    assert cal.fiscal_quarter == 2  # Apr-Jun


def test_fiscal_year_and_quarter_april_start():
    """Fiscal year and quarter with April start."""
    target_time = dt.datetime(2024, 3, 31)  # March 2024
    cal = Frist(target_time=target_time, fy_start_month=4).cal
    assert cal.fiscal_year == 2023  # Fiscal year starts in April
    assert cal.fiscal_quarter == 4  # Jan-Mar is Q4 for April start

    target_time = dt.datetime(2024, 4, 1)  # April 2024
    cal = Frist(target_time=target_time, fy_start_month=4).cal
    assert cal.fiscal_year == 2024
    assert cal.fiscal_quarter == 1  # Apr-Jun is Q1 for April start

    target_time = dt.datetime(2024, 7, 15)  # July 2024
    cal = Frist(target_time=target_time, fy_start_month=4).cal
    assert cal.fiscal_quarter == 2  # Jul-Sep is Q2 for April start

    target_time = dt.datetime(2024, 10, 1)  # October 2024
    cal = Frist(target_time=target_time, fy_start_month=4).cal
    assert cal.fiscal_quarter == 3  # Oct-Dec is Q3 for April start

    target_time = dt.datetime(2025, 1, 1)  # January 2025
    cal = Frist(target_time=target_time, fy_start_month=4).cal
    assert cal.fiscal_quarter == 4  # Jan-Mar is Q4 for April start