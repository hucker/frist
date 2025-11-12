"""
Test module for Cal.in_workdays functionality.

Covers scenarios with weekends, holidays, and various window ranges.
"""

import datetime as dt
import pytest
from frist import Cal

@pytest.mark.parametrize(
    "ref_date, target_date, holidays, start, end, expected, case",
    [
        # No holidays, target is Wednesday, window is Mon-Fri
        (
            dt.datetime(2024, 5, 6),  # Monday
            dt.datetime(2024, 5, 8),  # Wednesday
            set(),
            -2, 2,
            True,
            "midweek, no holidays"
        ),
        # Holiday on Wednesday, target is Wednesday, window is Mon-Fri
        (
            dt.datetime(2024, 5, 6),  # Monday
            dt.datetime(2024, 5, 8),  # Wednesday
            {"2024-05-08"},
            -2, 2,
            False,
            "midweek holiday, target is holiday"
        ),
        # Holiday on Wednesday, target is Thursday, window is Mon-Fri
        (
            dt.datetime(2024, 5, 6),  # Monday
            dt.datetime(2024, 5, 9),  # Thursday
            {"2024-05-08"},
            -2, 2,
            True,
            "midweek holiday, target is not holiday"
        ),
        # Holiday on Monday, target is Friday, window is Mon-Fri
        (
            dt.datetime(2024, 5, 6),  # Monday (holiday)
            dt.datetime(2024, 5, 10), # Friday
            {"2024-05-06"},
            0, 4,
            True,
            "holiday on first day, target is last day"
        ),
        # Holiday on Friday, target is Monday, window is Mon-Fri
        (
            dt.datetime(2024, 5, 6),  # Monday
            dt.datetime(2024, 5, 10), # Friday (holiday)
            {"2024-05-10"},
            0, 4,
            False,
            "holiday on last day, target is holiday"
        ),
        # Spanning weekend, target is next Monday, window is Fri-next Mon
        (
            dt.datetime(2024, 5, 10), # Friday
            dt.datetime(2024, 5, 13), # Next Monday
            set(),
            0, 1,
            True,
            "spanning weekend, target is next Monday"
        ),
        # Spanning weekend, target is Sunday, window is Fri-next Mon
        (
            dt.datetime(2024, 5, 10), # Friday
            dt.datetime(2024, 5, 12), # Sunday
            set(),
            0, 2,
            False,
            "spanning weekend, target is Sunday (not workday)"
        ),
        # Multiple holidays, target is Thursday, window is Mon-Fri
        (
            dt.datetime(2024, 5, 6),  # Monday
            dt.datetime(2024, 5, 9),  # Thursday
            {"2024-05-07", "2024-05-08"},
            -3, 3,
            True,
            "multiple holidays, target is Thursday"
        ),
    ]
)
def test_in_workdays_various_cases(
    ref_date: dt.datetime,
    target_date: dt.datetime,
    holidays: set[str],
    start: int,
    end: int,
    expected: bool,
    case: str,
) -> None:
    """
    AAA: Arrange, Act, Assert
    Arrange: Setup Cal with ref_date, target_date, holidays
    Act: Call in_workdays with start, end
    Assert: Result matches expected
    """
    # Arrange
    cal = Cal(target_date, ref_date, holidays=holidays)
    # Act
    result = cal.in_workdays(start, end)
    # Assert
    assert result is expected, f"Failed: {case}"
