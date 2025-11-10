"""
Test file for standalone Age functionality.

Tests the Age class as a standalone utility without file dependencies.
"""

import datetime as dt

import pytest

from frist import Age


def test_age_standalone_creation():
    """Test Age class creation without file dependency."""
    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)

    # Test standalone usage (no path)
    age = Age(None, timestamp, base_time)
    assert age.path is None
    assert age.timestamp == timestamp
    assert age.base_time == base_time


def test_age_time_calculations():
    """Test Age time unit calculations."""
    # 1 day difference
    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    age = Age(None, timestamp, base_time)

    # Test exact calculations
    assert age.seconds == 86400.0  # 24 * 60 * 60
    assert age.minutes == 1440.0  # 24 * 60
    assert age.hours == 24.0  # 24
    assert age.days == 1.0  # 1
    assert age.weeks == pytest.approx(1.0 / 7.0)
    assert age.months == pytest.approx(1.0 / 30.44)
    assert age.years == pytest.approx(1.0 / 365.25)


def test_age_fractional_calculations():
    """Test Age calculations with fractional time periods."""
    # 12 hours difference
    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time = dt.datetime(2024, 1, 2, 0, 0, 0)  # 12 hours later

    age = Age(None, timestamp, base_time)

    assert age.seconds == 43200.0  # 12 * 60 * 60
    assert age.minutes == 720.0  # 12 * 60
    assert age.hours == 12.0  # 12
    assert age.days == 0.5  # 0.5
    assert age.weeks == pytest.approx(0.5 / 7.0)


def test_age_parse_static_method():
    """Test Age.parse static method for string parsing."""
    # Test basic time units
    assert Age.parse("30") == 30.0  # seconds
    assert Age.parse("5m") == 300.0  # 5 minutes
    assert Age.parse("2h") == 7200.0  # 2 hours
    assert Age.parse("3d") == 259200.0  # 3 days
    assert Age.parse("1w") == 604800.0  # 1 week

    # Test longer units
    assert Age.parse("1y") == 31557600.0  # 1 year
    assert Age.parse("2months") == 5260032.0  # 2 months

    # Test decimal values
    assert Age.parse("1.5h") == 5400.0  # 1.5 hours
    assert Age.parse("2.5d") == 216000.0  # 2.5 days


def test_age_parse_case_insensitive():
    """Test that Age.parse is case insensitive."""
    assert Age.parse("5M") == 300.0  # uppercase M for minutes
    assert Age.parse("2H") == 7200.0  # uppercase H for hours
    assert Age.parse("3D") == 259200.0  # uppercase D for days
    assert Age.parse("1HOUR") == 3600.0  # uppercase full word
    assert Age.parse("2DAYS") == 172800.0  # uppercase plural


def test_age_parse_unit_variations():
    """Test Age.parse with different unit variations."""
    # Test minute variations
    assert Age.parse("5min") == 300.0
    assert Age.parse("5minute") == 300.0
    assert Age.parse("5minutes") == 300.0

    # Test hour variations
    assert Age.parse("2hr") == 7200.0
    assert Age.parse("2hour") == 7200.0
    assert Age.parse("2hours") == 7200.0

    # Test day variations
    assert Age.parse("3day") == 259200.0
    assert Age.parse("3days") == 259200.0

    # Test week variations
    assert Age.parse("1week") == 604800.0
    assert Age.parse("1weeks") == 604800.0


def test_age_parse_whitespace_handling():
    """Test Age.parse handles whitespace correctly."""
    assert Age.parse(" 5m ") == 300.0
    assert Age.parse("2 h") == 7200.0
    assert Age.parse(" 3  days ") == 259200.0


def test_age_parse_error_handling():
    """Test Age.parse error handling for invalid input."""
    with pytest.raises(ValueError, match="Invalid age format"):
        Age.parse("invalid")

    with pytest.raises(ValueError, match="Invalid age format"):
        Age.parse("5.5.5h")  # Multiple decimal points

    with pytest.raises(ValueError, match="Unknown unit"):
        Age.parse("5xyz")  # Invalid unit


def test_age_zero_time_difference():
    """Test Age calculations when timestamps are the same."""
    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time = dt.datetime(2024, 1, 1, 12, 0, 0)

    age = Age(None, timestamp, base_time)

    assert age.seconds == 0.0
    assert age.minutes == 0.0
    assert age.hours == 0.0
    assert age.days == 0.0
    assert age.weeks == 0.0
    assert age.months == 0.0
    assert age.years == 0.0


def test_age_negative_time_difference():
    """Test Age calculations when target is in the future."""
    # Target time is 1 day in the future
    timestamp: int|float = dt.datetime(2024, 1, 2, 12, 0, 0).timestamp()
    base_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)

    age:Age = Age(None, timestamp, base_time)

    # Should return negative values (future dates)
    assert age.seconds == -86400.0
    assert age.minutes == -1440.0
    assert age.hours == -24.0
    assert age.days == -1.0


def test_age_with_nonexistent_file_path():
    """Test Age with a file path that doesn't exist."""
    from pathlib import Path

    # Create a path to a file that definitely doesn't exist
    nonexistent_path = Path("/definitely/does/not/exist/nowhere.txt")

    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    age = Age(nonexistent_path, timestamp, base_time)

    # Should return 0 for all time units when file doesn't exist
    assert age.seconds == 0.0
    assert age.minutes == 0.0
    assert age.hours == 0.0
    assert age.days == 0.0
    assert age.weeks == 0.0
    assert age.months == 0.0
    assert age.years == 0.0

    # Path should be preserved
    assert age.path == nonexistent_path
