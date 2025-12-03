"""
Unit tests for fiscal year and fiscal quarter calculations in Chrono and Cal.

This file verifies:
- Default January and custom April fiscal year starts
- All fiscal year start months (1-12) for every month and every day in two years
- Quarter boundary transitions for a June fiscal year start

Each test is documented with its logic, expected results, and coverage rationale.
"""

import datetime as dt
import itertools
import pytest

from frist import Chrono, BizPolicy, Biz


def test_fiscal_year_and_quarter_january_start():
    """
    Test fiscal year and quarter calculation for the default January fiscal year start.
    Verifies:
    - February 2024 is in fiscal year 2024, Q1
    - April 2024 is in fiscal year 2024, Q2
    """
    # Arrange
    target_time = dt.datetime(2024, 2, 15)  # February 2024
    # Act
    biz:Biz = Chrono(target_time=target_time).biz
    # Assert
    assert biz.fiscal_year == 2024, "Fiscal year should be 2024 for Feb 2024 with January start"
    assert biz.fiscal_quarter == 1, "Fiscal quarter should be 1 (Jan-Mar) for Feb 2024 with January start"

    # Arrange
    target_time = dt.datetime(2024, 4, 1)  # April 2024
    # Act
    biz:Biz = Chrono(target_time=target_time).biz
    # Assert
    assert biz.fiscal_quarter == 2, "Fiscal quarter should be 2 (Apr-Jun) for April 2024 with January start"


def test_fiscal_year_and_quarter_april_start():
    """
    Test fiscal year and quarter calculation for an April fiscal year start.
    Verifies:
    - March 2024 is in fiscal year 2023, Q4
    - April 2024 is in fiscal year 2024, Q1
    - July 2024 is in Q2
    - October 2024 is in Q3
    - January 2025 is in Q4
    """
    # Arrange
    policy: BizPolicy = BizPolicy(fiscal_year_start_month=4)

    # Act
    target_time = dt.datetime(2024, 3, 31)  # March 2024
    biz:Biz = Chrono(target_time=target_time, policy=policy).biz
    # Assert
    assert biz.fiscal_year == 2023, "Fiscal year should be 2023 for Mar 2024 with April start"
    assert biz.fiscal_quarter == 4, "Fiscal quarter should be 4 (Jan-Mar) for Mar 2024 with April start"

    # Act
    target_time = dt.datetime(2024, 4, 1)  # April 2024
    biz = Chrono(target_time=target_time, policy=policy).biz
    # Assert
    assert biz.fiscal_year == 2024, "Fiscal year should be 2024 for Apr 2024 with April start"
    assert biz.fiscal_quarter == 1, "Fiscal quarter should be 1 (Apr-Jun) for Apr 2024 with April start"

    # Act
    target_time = dt.datetime(2024, 7, 15)  # July 2024
    biz:Biz = Chrono(target_time=target_time, policy=policy).biz
    # Assert
    assert biz.fiscal_quarter == 2, "Fiscal quarter should be 2 (Jul-Sep) for Jul 2024 with April start"

    # Act
    target_time = dt.datetime(2024, 10, 1)  # October 2024
    biz:Biz = Chrono(target_time=target_time,policy=policy).biz
    # Assert
    assert biz.fiscal_quarter == 3, "Fiscal quarter should be 3 (Oct-Dec) for Oct 2024 with April start"

    # Act
    target_time = dt.datetime(2025, 1, 1)  # January 2025
    biz:Biz = Chrono(target_time=target_time,policy=policy).biz
    # Assert
    assert biz.fiscal_quarter == 4, "Fiscal quarter should be 4 (Jan-Mar) for Jan 2025 with April start"


@pytest.mark.parametrize("fy_start_month", range(1, 13))
def test_fiscal_year_and_quarter_all_start_months(fy_start_month:int):
    """
    For each possible fiscal year start month (January through December),
    this test iterates through every month in two consecutive years (2024 and 2025).
    For each month, it constructs a Chrono/Cal object and verifies:

    - The fiscal year is correctly calculated: If the month is greater than or equal to the fiscal year start month,
      the fiscal year should be the current year; otherwise, it should be the previous year.
    - The fiscal quarter is correctly calculated: Quarters are determined by offsetting the month from the fiscal year start month,
      dividing by 3, and adding 1 (so each quarter is 3 months, starting from the fiscal year start month).

    This ensures that fiscal year and quarter logic is correct for all possible fiscal year start months and for all months in a year,
    including year boundaries and rollover cases.
    """
    # Arrange
    policy = BizPolicy(fiscal_year_start_month=fy_start_month)
    # Act & Assert
    for year, month in itertools.product([2024, 2025], range(1, 13)):
        day = 15  # Middle of the month
        target_time = dt.datetime(year, month, day)
        biz:Biz = Chrono(target_time=target_time, policy=policy).biz

        # Assert
        expected_fy = year if month >= fy_start_month else year - 1
        offset = (month - fy_start_month) % 12
        expected_fq = (offset // 3) + 1

        assert biz.fiscal_year == expected_fy, (
            f"FY start {fy_start_month}, date {target_time}: "
            f"Expected fiscal year {expected_fy}, got {biz.fiscal_year}"
        )
        assert biz.fiscal_quarter == expected_fq, (
            f"FY start {fy_start_month}, date {target_time}: "
            f"Expected fiscal quarter {expected_fq}, got {biz.fiscal_quarter}"
        )


@pytest.mark.parametrize("date_str, expected_fy, expected_fq", [
    # Q1: Jun-Aug
    ("2024-06-01", 2024, 1),  # First day Q1
    ("2024-08-31", 2024, 1),  # Last day Q1
    # Q2: Sep-Nov
    ("2024-09-01", 2024, 2),  # First day Q2
    ("2024-11-30", 2024, 2),  # Last day Q2
    # Q3: Dec-Feb
    ("2024-12-01", 2024, 3),  # First day Q3
    ("2025-02-28", 2024, 3),  # Last day Q3
    # Q4: Mar-May
    ("2025-03-01", 2024, 4),  # First day Q4
    ("2025-05-31", 2024, 4),  # Last day Q4
    # Next fiscal year
    ("2025-06-01", 2025, 1),  # First day Q1 next year
    ("2025-08-31", 2025, 1),  # Last day Q1 next year
])
def test_june_fiscal_year_quarter_boundaries(date_str: str, expected_fy: int, expected_fq: int):
    """
    Test fiscal year and quarter transitions for a June fiscal year start.
    This covers both the first and last day of each quarter boundary, so you can see exactly how 
    the logic works and transitions occur.
    Each case is parameterized for clarity and direct inspection of expected results.
    """
    # Arrange
    policy: BizPolicy = BizPolicy(fiscal_year_start_month=6)
    target_time:dt.datetime = dt.datetime.strptime(date_str, "%Y-%m-%d")
    # Act
    biz:Biz = Chrono(target_time=target_time, policy=policy).biz
    # Assert
    assert biz.fiscal_year == expected_fy, (
        f"Date {date_str}: Expected fiscal year {expected_fy}, got {biz.fiscal_year}"
    )
    assert biz.fiscal_quarter == expected_fq, (
        f"Date {date_str}: Expected fiscal quarter {expected_fq}, got {biz.fiscal_quarter}"
    )


@pytest.mark.parametrize("fy_start_month", range(1, 13))
def test_fiscal_year_and_quarter_all_days(fy_start_month: int):
    """
    This test is really the same as the last test but it iterates through every day in
    two consecutive years...but it calculates fiscal year and quarter (which might have a bug)
    but this saves me from having a table with 730 entries.
    """
    # Arrange
    policy: BizPolicy = BizPolicy(fiscal_year_start_month=fy_start_month)
    start_date: dt.datetime = dt.datetime(2024, 1, 1)
    end_date:dt.datetime = dt.datetime(2025, 12, 31)
    current_date:dt.datetime= start_date
    # Act & Assert
    while current_date <= end_date:
        target_time = dt.datetime.combine(current_date, dt.time(12, 0))
        biz = Chrono(target_time=target_time, policy=policy).biz

        year = current_date.year
        month = current_date.month

        # Assert
        expected_fy:int = year if month >= fy_start_month else year - 1
        offset:int = (month - fy_start_month) % 12
        expected_fq:int = (offset // 3) + 1

        assert biz.fiscal_year == expected_fy, (
            f"FY start {fy_start_month}, date {target_time}: "
            f"Expected fiscal year {expected_fy}, got {biz.fiscal_year}"
        )
        assert biz.fiscal_quarter == expected_fq, (
            f"FY start {fy_start_month}, date {target_time}: "
            f"Expected fiscal quarter {expected_fq}, got {biz.fiscal_quarter}"
        )
        current_date += dt.timedelta(days=1)