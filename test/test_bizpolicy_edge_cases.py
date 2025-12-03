"""
Test suite for BizPolicy edge cases, error handling, and parameter validation.

Covers:
- Fiscal year/quarter boundaries
"""

import datetime as dt
import pytest
from frist import Chrono, BizPolicy

def test_fiscal_boundary_crossing() -> None:
    """Test fiscal year/quarter boundaries using BizPolicy."""
    # Arrange
    policy_july: BizPolicy = BizPolicy(fiscal_year_start_month=7)

    # Act
    target_time_june: dt.datetime = dt.datetime(2024, 6, 30)  # June 2024
    chrono_june: Chrono = Chrono(target_time=target_time_june, policy=policy_july)
    # Assert
    expected_fiscal_year_june = 2023
    expected_fiscal_quarter_june = 4
    actual_fiscal_year_june = chrono_june.biz.fiscal_year
    actual_fiscal_quarter_june = chrono_june.biz.fiscal_quarter
    assert actual_fiscal_year_june == expected_fiscal_year_june, (
        f"Expected fiscal year {expected_fiscal_year_june} for June, "
        f"got {actual_fiscal_year_june}"
    )
    assert actual_fiscal_quarter_june == expected_fiscal_quarter_june, (
        f"Expected fiscal quarter {expected_fiscal_quarter_june} for June, "
        f"got {actual_fiscal_quarter_june}"
    )

    # Act
    target_time_july: dt.datetime = dt.datetime(2024, 7, 1)  # July 2024
    chrono_july: Chrono = Chrono(target_time=target_time_july, policy=policy_july)
    # Assert
    expected_fiscal_year_july = 2024
    expected_fiscal_quarter_july = 1
    actual_fiscal_year_july = chrono_july.biz.fiscal_year
    actual_fiscal_quarter_july = chrono_july.biz.fiscal_quarter
    assert actual_fiscal_year_july == expected_fiscal_year_july, (
        f"Expected fiscal year {expected_fiscal_year_july} for July, "
        f"got {actual_fiscal_year_july}"
    )
    assert actual_fiscal_quarter_july == expected_fiscal_quarter_july, (
        f"Expected fiscal quarter {expected_fiscal_quarter_july} for July, "
        f"got {actual_fiscal_quarter_july}"
    )
