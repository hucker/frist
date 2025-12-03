"""
Tests for YearNamespace in frist._ranges.py
"""

import datetime as dt
import pytest
from frist import Cal
from frist._ranges import YearNamespace

@pytest.mark.parametrize(
    "target_date, expected_day_of_year",
    [
        (dt.datetime(2024, 1, 1), 1),
        (dt.datetime(2024, 2, 1), 32),
        (dt.datetime(2024, 12, 31), 366),  # 2024 is a leap year
        (dt.datetime(2023, 12, 31), 365),  # 2023 is not a leap year
    ]
)
def test_year_namespace_day_of_year(target_date: dt.datetime,
                                   expected_day_of_year: int) -> None:
    """
    Test YearNamespace.day_of_year returns correct day of year.
    """
    # Arrange
    cal = Cal(target_date, target_date)
    yn = YearNamespace(cal)
    # Act
    actual = yn.day_of_year()
    expected = expected_day_of_year
    # Assert
    msg = f"{target_date:%Y-%m-%d}: actual={actual}, expected={expected}"
    assert actual == expected, msg

@pytest.mark.parametrize(
    "target_date, n, expected",
    [
        (dt.datetime(2024, 1, 1), 1, True),
        (dt.datetime(2024, 2, 1), 32, True),
        (dt.datetime(2024, 12, 31), 366, True),
        (dt.datetime(2024, 12, 31), 365, False),
        (dt.datetime(2023, 12, 31), 365, True),
        (dt.datetime(2023, 12, 31), 366, False),
    ]
)
def test_year_namespace_is_day_of_year(target_date: dt.datetime, n: int, expected: bool) -> None:
    """
    Test YearNamespace.is_day_of_year returns True only for correct day.
    """
    # Arrange
    cal = Cal(target_date, target_date)
    yn = YearNamespace(cal)
    # Act
    actual = yn.is_day_of_year(n)
    # Assert
    msg = (
        f"{target_date:%Y-%m-%d} is_day_of_year({n}): actual={actual}, expected={expected}"
    )
    assert actual is expected, msg
