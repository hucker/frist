"""
Comprehensive tests for the Age.format() method.

Verifies that Age.format() returns human-friendly strings for time intervals
in the most appropriate units, including fractional values and exact decimal formatting.
Uses non-leap years for month calculations so 14.00 days is exactly half a month.
"""

import datetime as dt
import pytest

from frist._age import Age

@pytest.mark.parametrize(
    "start, end, expected",
    [
        # Seconds (exact decimal, <45s)
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 0, 0, 30), "30.00 seconds"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 0, 0, 44), "44.00 seconds"),
        # Minutes (>=45s and <45m)
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 0, 0, 45), "0.75 minutes"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 0, 31, 30), "31.50 minutes"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 0, 44, 59), "44.98 minutes"),
        # Hours (>=45m and <22h)
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 0, 45, 0), "0.75 hours"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 12, 0, 0), "12.00 hours"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 1, 21, 30, 0), "21.50 hours"),
        # Days (>=22h and <26d)
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 2, 18, 0, 0), "1.75 days"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 15, 0, 0, 0), "14.00 days"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 1, 26, 0, 0, 0), "25.00 days"),
        # Months (>=26d and <11mo)
        # 14 days in a 28-day February = 0.5 months
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 2, 15, 0, 0, 0), "1.50 months"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 2, 1, 0, 0, 0), "1.00 months"),
        (dt.datetime(2023, 1, 1, 0, 0, 0), dt.datetime(2023, 11, 16, 0, 0, 0), "10.50 months"),
        # Years (>=11mo)
        (dt.datetime(2020, 1, 1), dt.datetime(2023, 1, 1), "3.00 years"),
        (dt.datetime(2021, 1, 1), dt.datetime(2023, 7, 1), "2.50 years"),
        # Negative interval (should use same logic)
        (dt.datetime(2023, 1, 2), dt.datetime(2023, 1, 1), "-1.00 days"),
        (dt.datetime(2023, 2, 15), dt.datetime(2023, 1, 1), "-1.50 months"),
    ]
)
def test_age_format_default(
    start: dt.datetime, end: dt.datetime, expected: str
) -> None:
    """
    Test Age.format() with default formatting and thresholds, including decimals.
    
    NOTE: 

    """
    # Arrange
    age = Age(start, end)
    # Act
    actual = age.format()
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"

def test_age_format_custom_units() -> None:
    """Test Age.format() with custom units and formatting, including decimals."""
    # Arrange
    start: dt.datetime = dt.datetime(2023, 1, 1)
    end: dt.datetime = dt.datetime(2023, 1, 1, 5, 15, 0)  # 5 hours, 15 minutes = 315 minutes
    age = Age(start, end)
    custom_units = [
        (120, "s", lambda self: self.seconds),
        (400, "m", lambda self: self.minutes),
        (48, "h", lambda self: self.hours),
    ]
    # Act
    actual = age.format(units=custom_units, fmt="{value:.2f}{unit}")
    # Assert
    expected = "315.00m"
    assert actual == expected, f"Expected '{expected}', got '{actual}'"