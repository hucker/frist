"""Explicit checks for Biz compact unit namespaces.

These tests exercise a concrete `Biz` instance where `target_time == ref_time`.
They assert expected True/False membership for offset 0 and a simple negative
offset for each unit.
"""

import datetime as dt

from frist._biz import Biz


def test_biz_unit_namespace_explicit_checks():
    # Arrange
    # Use a weekday (Friday) so business/working-day checks are True
    ref = dt.datetime(2025, 3, 14, 12, 34, 56)
    biz = Biz(target_time=ref, ref_time=ref)

    # Act / Assert: business days
    assert biz.bday.in_(0) is True
    assert biz.bday.in_(-1) is False

    # Act / Assert: working days
    assert biz.wday.in_(0) is True
    assert biz.wday.in_(-1) is False

    # Act / Assert: fiscal quarters
    assert biz.fqtr.in_(0) is True
    assert biz.fqtr.in_(-1) is False

    # Act / Assert: fiscal years
    assert biz.fyr.in_(0) is True
    assert biz.fyr.in_(-1) is False
