"""
Test file for standalone Age functionality.

Tests the Age class as a standalone utility without file dependencies.
"""

import datetime as dt
import pytest
from frist import Age, CalendarPolicy


@pytest.mark.parametrize(
    "start, end, combo_msg, expected_seconds, expected_days",
    [
        (
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            "datetime/datetime",
            86400.0,
            1.0,
        ),
        (
            dt.datetime(2024, 1, 1, 12, 0, 0).timestamp(),
            dt.datetime(2024, 1, 2, 12, 0, 0),
            "timestamp/datetime",
            86400.0,
            1.0,
        ),
        (
            dt.datetime(2024, 1, 1, 12, 0, 0),
            dt.datetime(2024, 1, 2, 12, 0, 0).timestamp(),
            "datetime/timestamp",
            86400.0,
            1.0,
        ),
        (
            dt.datetime(2024, 1, 1, 12, 0, 0).timestamp(),
            dt.datetime(2024, 1, 2, 12, 0, 0).timestamp(),
            "timestamp/timestamp",
            86400.0,
            1.0,
        ),
    ],
)
def test_age_start_end_time_combinations(
    start: dt.datetime | float,
    end: dt.datetime | float,
    combo_msg: str,
    expected_seconds: float,
    expected_days: float,
) -> None:
    """Test Age handles all combinations of start/end as timestamps or datetimes."""
    # Arrange: Inputs are parameterized above

    # Act: Create Age instance
    age = Age(start, end)

    # Assert: Check seconds and days match expectations
    assert age.seconds == expected_seconds, f"Failed for {combo_msg}"
    assert age.days == expected_days, f"Failed for {combo_msg}"


def test_age_time_calculations():
    """Test Age time unit calculations."""
    # Arrange
    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    # Act
    age = Age(timestamp, base_time)

    # Assert
    assert age.seconds == 86400.0
    assert age.minutes == 1440.0
    assert age.hours == 24.0
    assert age.days == 1.0
    assert age.weeks == pytest.approx(1.0 / 7.0)  # type: ignore
    assert age.months == pytest.approx(1.0 / 30.44)  # type: ignore
    assert age.years == pytest.approx(1.0 / 365.25)  # type: ignore


def test_age_fractional_calculations():
    """Test Age calculations with fractional time periods."""
    # Arrange
    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time = dt.datetime(2024, 1, 2, 0, 0, 0)

    # Act
    age = Age(timestamp, base_time)

    # Assert
    assert age.seconds == 43200.0
    assert age.minutes == 720.0
    assert age.hours == 12.0
    assert age.days == 0.5
    assert age.weeks == pytest.approx(0.5 / 7.0)


def test_age_parse_static_method():
    """Test Age.parse static method for string parsing."""
    # Arrange/Act/Assert (combined for static method)
    assert Age.parse("30") == 30.0
    assert Age.parse("5m") == 300.0
    assert Age.parse("2h") == 7200.0
    assert Age.parse("3d") == 259200.0
    assert Age.parse("1w") == 604800.0
    assert Age.parse("1y") == 31557600.0
    assert Age.parse("2months") == 5260032.0
    assert Age.parse("1.5h") == 5400.0
    assert Age.parse("2.5d") == 216000.0


def test_age_parse_case_insensitive():
    """Test that Age.parse is case insensitive."""
    # Arrange/Act/Assert
    assert Age.parse("5M") == 300.0
    assert Age.parse("2H") == 7200.0
    assert Age.parse("3D") == 259200.0
    assert Age.parse("1HOUR") == 3600.0
    assert Age.parse("2DAYS") == 172800.0


def test_age_parse_unit_variations():
    """Test Age.parse with different unit variations."""
    # Arrange/Act/Assert
    assert Age.parse("5min") == 300.0
    assert Age.parse("5minute") == 300.0
    assert Age.parse("5minutes") == 300.0
    assert Age.parse("2hr") == 7200.0
    assert Age.parse("2hour") == 7200.0
    assert Age.parse("2hours") == 7200.0
    assert Age.parse("3day") == 259200.0
    assert Age.parse("3days") == 259200.0
    assert Age.parse("1week") == 604800.0
    assert Age.parse("1weeks") == 604800.0


def test_age_parse_whitespace_handling():
    """Test Age.parse handles whitespace correctly."""
    # Arrange/Act/Assert
    assert Age.parse(" 5m ") == 300.0
    assert Age.parse("2 h") == 7200.0
    assert Age.parse(" 3  days ") == 259200.0


def test_age_parse_error_handling():
    """Test Age.parse error handling for invalid input."""
    # Arrange/Act/Assert
    with pytest.raises(ValueError, match="Invalid age format"):
        Age.parse("invalid")
    with pytest.raises(ValueError, match="Invalid age format"):
        Age.parse("5.5.5h")
    with pytest.raises(ValueError, match="Unknown unit"):
        Age.parse("5xyz")


def test_age_zero_time_difference():
    """Test Age calculations when timestamps are the same."""
    # Arrange
    timestamp = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    base_time = dt.datetime(2024, 1, 1, 12, 0, 0)

    # Act
    age = Age(timestamp, base_time)

    # Assert
    assert age.seconds == 0.0
    assert age.minutes == 0.0
    assert age.hours == 0.0
    assert age.days == 0.0
    assert age.weeks == 0.0
    assert age.months == 0.0
    assert age.years == 0.0


def test_age_negative_time_difference():
    """Test Age calculations when target is in the future."""
    # Arrange
    timestamp: int | float = dt.datetime(2024, 1, 2, 12, 0, 0).timestamp()
    base_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)

    # Act
    age: Age = Age(timestamp, base_time)

    # Assert
    assert age.seconds == -86400.0
    assert age.minutes == -1440.0
    assert age.hours == -24.0
    assert age.days == -1.0


@pytest.mark.parametrize(
    "number,unit,expected_seconds",
    [
        (5, "m", 300.0),
        (2, "h", 7200.0),
        (3, "d", 259200.0),
        (1, "w", 604800.0),
        (1, "y", 31557600.0),
        (2, "months", 5260032.0),
        (1.5, "h", 5400.0),
        (2.5, "d", 216000.0),
        (30, "", 30.0),
        (-5, "m", -300.0),
        (-2, "h", -7200.0),
        (-3, "d", -259200.0),
        (-1, "w", -604800.0),
        (-1, "y", -31557600.0),
        (-2, "months", -5260032.0),
        (-1.5, "h", -5400.0),
        (-2.5, "d", -216000.0),
        (-30, "", -30.0),
    ],
)
def test_age_parse_with_spaces_and_negatives(
    number: float,
    unit: str,
    expected_seconds: float
) -> None:
    # Arrange
    patterns = [
        f"{number}{unit}",
        f" {number}{unit}",
        f"{number} {unit}",
        f"{number}{unit} ",
        f" {number} {unit} ",
        f"  {number}  {unit}  ",
    ]
    # Act & Assert
    for pattern in patterns:
        assert Age.parse(pattern) == expected_seconds


def test_age_init_invalid_start_type() -> None:
    """Arrange, Act, Assert
    Arrange: Provide invalid start_time type
    Act & Assert: TypeError is raised
    """
    import pytest
    with pytest.raises(TypeError, match="start_time must be datetime, float, or int"):
        Age("not-a-date") # type: ignore # Exception expected

def test_age_init_invalid_end_type() -> None:
    """Arrange, Act, Assert
    Arrange: Provide invalid end_time type
    Act & Assert: TypeError is raised
    """
    import pytest
    with pytest.raises(TypeError, match="end_time must be datetime, float, int, or None"):
        Age(dt.datetime.now(), "not-a-date") # type: ignore # Exception expected

def test_age_parse_invalid_format() -> None:
    """Arrange, Act, Assert
    Arrange: Provide invalid age string
    Act & Assert: ValueError is raised
    """
    import pytest
    with pytest.raises(ValueError, match="Invalid age format"):
        Age.parse("bad-format")

def test_age_parse_unknown_unit() -> None:
    """Arrange, Act, Assert
    Arrange: Provide age string with unknown unit
    Act & Assert: ValueError is raised
    """
    import pytest
    with pytest.raises(ValueError, match="Unknown unit"):
        Age.parse("5fortnights")


def test_age_end_time_defaults_to_now() -> None:
    """Arrange, Act, Assert
    Arrange: Create Age with only start_time
    Act: Get age in seconds
    Assert: Age end_time is close to now
    """
    import time
    start = dt.datetime.now()
    age = Age(start)
    # Sleep briefly to ensure a measurable age
    time.sleep(0.01)
    now = dt.datetime.now()
    assert (now - age.end_time).total_seconds() < 0.1, "end_time should default to current time"
    assert age.end_time >= start, "end_time should be after start_time"


def test_working_days_basic_weekday() -> None:
    """Age.working_days returns 1.0 for a full weekday."""
    start = dt.datetime(2024, 1, 2, 0, 0, 0)  # Tuesday
    end = dt.datetime(2024, 1, 2, 23, 59, 59)
    age = Age(start, end)
    assert abs(age.working_days - 1.0) < 1e-6, "Should be 1.0 for full weekday"


def test_working_days_weekend() -> None:
    """Age.working_days returns 0.0 for a weekend day."""
    start = dt.datetime(2024, 1, 6, 0, 0, 0)  # Saturday
    end = dt.datetime(2024, 1, 6, 23, 59, 59)
    age = Age(start, end)
    assert age.working_days == 0.0, "Should be 0.0 for weekend"


def test_working_days_partial_day() -> None:
    start: dt.datetime
    end: dt.datetime
    """Age.working_days returns correct fraction for partial weekday."""
    start = dt.datetime(2024, 1, 2, 12, 0, 0)  # Tuesday noon
    end = dt.datetime(2024, 1, 2, 18, 0, 0)
    age = Age(start, end)
    # Business hours: 9:00 to 17:00 (8 hours)
    # Noon to 17:00 = 5 hours (within business hours)
    # 17:00 to 18:00 is outside business hours, so only noon to 17:00 counts
    expected = 5 / 8  # 5 hours out of 8 business hours
    assert abs(age.working_days - expected) < 1e-6, "Should match fraction of business hours"


def test_working_days_multiple_days() -> None:
    start: dt.datetime
    end: dt.datetime
    """Age.working_days sums multiple weekdays, skips weekends."""
    start = dt.datetime(2024, 1, 5, 12, 0, 0)  # Friday noon
    end = dt.datetime(2024, 1, 8, 12, 0, 0)    # Monday noon
    age = Age(start, end)
    # Friday: half day, Saturday/Sunday: 0, Monday: half day
    expected = 0.5 + 0.5
    assert abs(age.working_days - expected) < 1e-6, "Should sum only working day fractions"


def test_working_days_holiday() -> None:
    cal: CalendarPolicy
    start: dt.datetime
    end: dt.datetime
    """Age.working_days returns 0.0 for a holiday (using custom CalendarPolicy)."""
    from frist._cal_policy import CalendarPolicy
    # Jan 2, 2024 is a holiday
    cal = CalendarPolicy(holidays={"2024-01-02"})
    start = dt.datetime(2024, 1, 2, 0, 0, 0)
    end = dt.datetime(2024, 1, 2, 23, 59, 59)
    age = Age(start, end, cal_policy=cal)
    assert age.working_days == 0.0, "Should be 0.0 for holiday"


def test_working_days_start_after_end() -> None:
    start: dt.datetime
    end: dt.datetime
    """Age.working_days returns 0.0 if start_time > end_time."""
    start = dt.datetime(2024, 1, 3, 12, 0, 0)
    end = dt.datetime(2024, 1, 2, 12, 0, 0)
    import pytest
    age = Age(start, end)
    with pytest.raises(ValueError, match="start_time must not be after end_time"):
        _ = age.working_days


def test_set_times_invalid_start_type() -> None:
    """
    Arrange: Create Age object, call set_times with invalid start_time type
    Act & Assert: TypeError is raised
    """
    age = Age(dt.datetime(2020, 1, 1), dt.datetime(2021, 1, 1))
    with pytest.raises(TypeError, match="start_time must be datetime, float, or int"):
        age.set_times(start_time="not-a-date") # type: ignore

def test_set_times_invalid_end_type() -> None:
    """
    Arrange: Create Age object, call set_times with invalid end_time type
    Act & Assert: TypeError is raised
    """
    age = Age(dt.datetime(2020, 1, 1), dt.datetime(2021, 1, 1))
    with pytest.raises(TypeError, match="end_time must be datetime, float, int, or None"):
        age.set_times(end_time="not-a-date") # type: ignore
