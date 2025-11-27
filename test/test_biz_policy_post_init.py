"""
Unit tests for BizPolicy __post_init__ validation.

Verifies that invalid fiscal_year_start_month and workdays values raise exceptions.
"""
import pytest
from frist._biz_policy import BizPolicy

def test_valid_calendar_policy() -> None:
    """
    Test that valid fiscal_year_start_month and workdays do not raise exceptions.
    """
    # Should not raise
    BizPolicy(fiscal_year_start_month=1, workdays=[0, 1, 2, 3, 4])
    BizPolicy(fiscal_year_start_month=12, workdays=[0, 6])
    BizPolicy(fiscal_year_start_month=6, workdays=[])
    BizPolicy(fiscal_year_start_month=7, workdays=[0, 1, 2, 3, 4, 5, 6])

def test_invalid_fiscal_year_start_month() -> None:
    """
    Test that invalid fiscal_year_start_month values raise ValueError.
    """
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        BizPolicy(fiscal_year_start_month=0)
    with pytest.raises(ValueError, match="fiscal_year_start_month must be in 1..12"):
        BizPolicy(fiscal_year_start_month=13)

def test_invalid_workdays_length() -> None:
    """
    Test that workdays longer than 7 raise ValueError.
    """
    with pytest.raises(ValueError, match="workdays must have 0 to 7 values"):
        BizPolicy(workdays=list(range(8)))

def test_invalid_workdays_values() -> None:
    """
    Test that workdays with values outside 0..6 raise ValueError.
    """
    with pytest.raises(ValueError, match="workdays must contain only integers 0..6"):
        BizPolicy(workdays=[-1, 0, 1])
    with pytest.raises(ValueError, match="workdays must contain only integers 0..6"):
        BizPolicy(workdays=[0, 1, 2, 3, 4, 5, 7])
    with pytest.raises(ValueError, match="workdays must have 0 to 7 values, got 8"):
        BizPolicy(workdays=[0, 1, 2, 3, 4, 5, 6, 7])
    assert True  # To indicate the test passed if no exceptions were raised
