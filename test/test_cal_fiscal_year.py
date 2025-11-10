"""
Tests for Cal.get_fiscal_year and Cal.get_fiscal_quarter static methods.
Verifies correct fiscal year and quarter calculation for various months and fiscal year starts.
Follows Frist CODESTYLE.md: AAA comments, parameterized cases, clear assertions.
"""
import datetime as dt

import pytest

from frist import Frist
from frist._cal import Cal


@pytest.mark.parametrize("dt_val, fy_start_month, expected_fy", [
    (dt.datetime(2024, 1, 1), 1, 2024),   # Jan, FY starts Jan
    (dt.datetime(2024, 3, 31), 1, 2024),  # Mar, FY starts Jan
    (dt.datetime(2024, 4, 1), 4, 2024),   # Apr, FY starts Apr
    (dt.datetime(2024, 3, 31), 4, 2023),  # Mar, FY starts Apr
    (dt.datetime(2024, 12, 31), 4, 2024), # Dec, FY starts Apr
    (dt.datetime(2025, 3, 31), 4, 2024),  # Mar next year, FY starts Apr
    (dt.datetime(2025, 4, 1), 4, 2025),   # Apr next year, FY starts Apr
])
def test_get_fiscal_year(dt_val, fy_start_month, expected_fy):
    """AAA: Test Cal.get_fiscal_year static method for various fiscal year starts."""
    # Act
    fy = Cal.get_fiscal_year(dt_val, fy_start_month)
    # Assert
    assert fy == expected_fy, f"Fiscal year for {dt_val} with FY start {fy_start_month} should be {expected_fy}, got {fy}"

@pytest.mark.parametrize("dt_val, fy_start_month, expected_fq", [
    (dt.datetime(2024, 1, 1), 1, 1),   # Jan, FY starts Jan, Q1
    (dt.datetime(2024, 4, 1), 1, 2),   # Apr, FY starts Jan, Q2
    (dt.datetime(2024, 7, 1), 1, 3),   # Jul, FY starts Jan, Q3
    (dt.datetime(2024, 10, 1), 1, 4),  # Oct, FY starts Jan, Q4
    (dt.datetime(2024, 4, 1), 4, 1),   # Apr, FY starts Apr, Q1
    (dt.datetime(2024, 7, 1), 4, 2),   # Jul, FY starts Apr, Q2
    (dt.datetime(2024, 10, 1), 4, 3),  # Oct, FY starts Apr, Q3
    (dt.datetime(2025, 1, 1), 4, 4),   # Jan, FY starts Apr, Q4
])
def test_get_fiscal_quarter(dt_val, fy_start_month, expected_fq):
    """AAA: Test Cal.get_fiscal_quarter static method for various fiscal year starts."""
    # Act
    fq = Cal.get_fiscal_quarter(dt_val, fy_start_month)
    # Assert
    assert fq == expected_fq, f"Fiscal quarter for {dt_val} with FY start {fy_start_month} should be {expected_fq}, got {fq}"

