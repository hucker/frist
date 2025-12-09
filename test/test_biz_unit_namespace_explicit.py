"""Explicit checks for Biz compact unit units.

These tests exercise a concrete `Biz` instance where `target_time == ref_time`.
They assert expected True/False membership for offset 0 and a simple negative
offset for each unit.
"""

import datetime as dt

from frist._biz import Biz


def test_biz_unit_unit_explicit_checks():
    """
    Explicit membership checks for Biz unit adapters.

    Verifies that for a Biz instance with target and reference set to a weekday (Friday),
    each unit namespace (`biz_day`, `work_day`, `fis_qtr`, `fis_year`) returns True for
    in_(0) and False for in_(-1), confirming correct window membership logic.
    """
    
    # Arrange
    # Use a weekday (Friday) so business/working-day checks are True
    ref = dt.datetime(2025, 3, 14, 12, 34, 56)
    biz = Biz(target_dt=ref, ref_dt=ref)

    # Act / Assert: business days
    assert biz.biz_day.in_(0) is True
    assert biz.biz_day.in_(-1) is False

    # Act / Assert: working days
    assert biz.work_day.in_(0) is True
    assert biz.work_day.in_(-1) is False

    # Act / Assert: fiscal quarters
    assert biz.fis_qtr.in_(0) is True
    assert biz.fis_qtr.in_(-1) is False

    # Act / Assert: fiscal years
    assert biz.fis_year.in_(0) is True
    assert biz.fis_year.in_(-1) is False
