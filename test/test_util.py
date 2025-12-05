"""
Utility tests for helpers and normalization in frist.
"""

import pytest

import datetime as dt
from frist._util import in_half_open, in_half_open_dt, in_half_open_date


def test_in_half_open_int():
    assert in_half_open(0, 0, 1) is True
    assert in_half_open(0, 1, 1) is False
    assert in_half_open(-2, -1, 0) is True


def test_in_half_open_dt():
    start = dt.datetime(2025, 1, 1, 0, 0)
    end = dt.datetime(2025, 1, 2, 0, 0)
    assert in_half_open_dt(start, start, end) is True
    assert in_half_open_dt(start, end, end) is False


def test_in_half_open_date():
    start = dt.date(2025, 1, 1)
    end = dt.date(2025, 1, 2)
    assert in_half_open_date(start, start, end) is True
    assert in_half_open_date(start, end, end) is False