"""
Unit tests for the MonthUnit class.
Covers core methods and edge cases for direct usage.
"""

import datetime as dt

import pytest

from frist import Cal
from frist.units import MonthUnit


def test_month_unit_in_impl_basic():
    """
    Test _in_impl for current, previous, and next month.
    """
    # Arrange
    cal = Cal(dt.datetime(2024, 3, 15), dt.datetime(2024, 3, 15))
    mn: MonthUnit = MonthUnit(cal)
    # Act & Assert
    assert mn.in_(0, 1), "Should be in current month (0 offset)"
    assert not mn.in_(-1, 0), "Should not be in previous month"
    assert not mn.in_(1, 2), "Should not be in next month"


@pytest.mark.parametrize(
    "dt_value, expected, msg",
    [
        (dt.datetime(2024, 3, 1), 2024 * 12 + 3, "Mar/2024 should be 2024*12+3"),
        (dt.datetime(2024, 12, 31), 2024 * 12 + 12, "Dec/2024 should be 2024*12+12"),
    ]
)
def test_month_unit_month_index(dt_value:dt.datetime, expected:int, msg:str):
    """
    Parametrized test for _month_index, including assert message.
    """
    # Arrange
    cal = Cal(dt.datetime(2024, 3, 15), dt.datetime(2024, 3, 15))
    mn = MonthUnit(cal)
    # Act & Assert
    assert mn._month_index(dt_value) == expected, msg


@pytest.mark.parametrize(
    "ref_date, weekday, n, expected",
    [
        # March 2024 Fridays
        (dt.datetime(2024, 3, 1), "friday", 1, dt.datetime(2024, 3, 1)),
        (dt.datetime(2024, 3, 1), "friday", 2, dt.datetime(2024, 3, 8)),
        (dt.datetime(2024, 3, 1), "friday", -1, dt.datetime(2024, 3, 29)),
        (dt.datetime(2024, 3, 1), "friday", -2, dt.datetime(2024, 3, 22)),
        # Feb 2024: 5th and -5th Friday do not exist (should raise)
        (dt.datetime(2024, 2, 1), "friday", 5, None),
        (dt.datetime(2024, 2, 1), "friday", -5, None),
    ],
)
def test_month_unit_nth_weekday_param(
    ref_date: dt.datetime,
    weekday: str,
    n: int,
    expected: dt.datetime | None,
) -> None:
    """
    Parametrized test for nth_weekday with positive and negative indexes, including error cases.
    """
    # Arrange
    cal = Cal(ref_date, ref_date)
    mn = MonthUnit(cal)
    # Act & Assert
    if expected is not None:
        assert mn.nth_weekday(weekday, n) == expected, (
            f"{n} {weekday} in {ref_date:%B %Y} should be {expected:%Y-%m-%d}, got {mn.nth_weekday(weekday, n)}"
        )
    else:
        with pytest.raises(ValueError):
            mn.nth_weekday(weekday, n)


@pytest.mark.parametrize(
    "ref_date, target_date, weekday, n, expected",
    [
        # March 2024 Fridays
        (dt.datetime(2024, 3, 1), dt.datetime(2024, 3, 1), "friday", 1, True),
        (dt.datetime(2024, 3, 1), dt.datetime(2024, 3, 1), "friday", 2, False),
        (dt.datetime(2024, 3, 1), dt.datetime(2024, 3, 29), "friday", -1, True),
        (dt.datetime(2024, 3, 1), dt.datetime(2024, 3, 22), "friday", -2, True),
        # Feb 2024: 5th and -5th Friday do not exist
        (dt.datetime(2024, 2, 1), dt.datetime(2024, 2, 23), "friday", 5, False),
        (dt.datetime(2024, 2, 1), dt.datetime(2024, 2, 23), "friday", -5, False),
    ],
)
def test_monthunit_is_nth_weekday_param(
    ref_date: dt.datetime,
    target_date: dt.datetime,
    weekday: str,
    n: int,
    expected: bool,
) -> None:
    """
    Parametrized test for is_nth_weekday with positive and negative indexes, including error cases.
    AAA: Arrange, Act, Assert.
    """
    # Arrange
    cal = Cal(target_date, ref_date)
    mn = MonthUnit(cal)
    # Act & Assert
    result = mn.is_nth_weekday(weekday, n)
    assert result is expected, (
        f"is_nth_weekday({weekday}, {n}) for target {target_date:%Y-%m-%d} in {ref_date:%B %Y} "
        f"should be {expected}, got {result}"
    )
