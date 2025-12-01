"""
Test file for standalone Age functionality.

Tests the Age class as a standalone utility without file dependencies.
"""

import datetime as dt
import pytest
from frist import Age


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
    assert age.weeks == pytest.approx(0.5 / 7.0) # type: ignore


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
    assert age.seconds == -86400.0, "Age seconds should be -86400 for 1 day difference"
    assert age.minutes == -1440.0, "Age minutes should be -1440 for 1 day difference"
    assert age.hours == -24.0, "Age hours should be -24 for 1 day difference"
    assert age.days == -1.0, "Age days should be -1 for 1 day difference"


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
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Age("not-a-date") # type: ignore # Exception expected

def test_age_init_invalid_end_type() -> None:
    """Arrange, Act, Assert
    Arrange: Provide invalid end_time type
    Act & Assert: TypeError is raised
    """
    import pytest
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
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


def test_set_times_invalid_start_type() -> None:
    """
    Arrange: Create Age object, call set_times with invalid start_time type
    Act & Assert: TypeError is raised
    """
    age = Age(dt.datetime(2020, 1, 1), dt.datetime(2021, 1, 1))
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        age.set_times(start_time="not-a-date") # type: ignore

def test_set_times_invalid_end_type() -> None:
    """
    Arrange: Create Age object, call set_times with invalid end_time type
    Act & Assert: TypeError is raised
    """
    age = Age(dt.datetime(2020, 1, 1), dt.datetime(2021, 1, 1))
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        age.set_times(end_time="not-a-date") # type: ignore


def test_age_with_dates():
    """Age correctly handles date inputs and calculates 24 hours for one day apart."""
    # Arrange
    start_date = dt.date(2025, 1, 1)
    end_date = dt.date(2025, 1, 2)
    
    # Act
    age = Age(start_date, end_date)
    
    # Assert
    assert age.days == 1.0, "Age should be 1 day for date inputs one day apart"
    assert age.hours == 24.0, "Age should be 24 hours for date inputs one day apart"


@pytest.mark.parametrize("start, end", [
    (dt.date(2025, 1, 1), dt.date(2025, 1, 2)),
    (dt.date(2025, 1, 1), dt.datetime(2025, 1, 2, 0, 0, 0)),
    (dt.datetime(2025, 1, 1, 0, 0, 0), dt.date(2025, 1, 2)),
])
def test_age_with_mixed_date_types(start, end):
    """Age correctly handles mixed date/datetime inputs."""
    # Arrange & Act
    age = Age(start, end)
    
    # Assert
    assert age.days == 1.0, "Age should be 1 day for inputs one day apart"
    assert age.hours == 24.0, "Age should be 24 hours for inputs one day apart"


def test_age_timezone_not_supported():
    """Age raises TypeError for timezone-aware datetimes."""
    # Arrange
    tz_dt = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    
    # Act & Assert
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Age(tz_dt)
    
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Age(dt.datetime(2025, 1, 1), tz_dt)
    
    # Also for set_times
    age = Age(dt.datetime(2020, 1, 1), dt.datetime(2021, 1, 1))
    with pytest.raises(TypeError, match="Timezones are not supported"):
        age.set_times(start_time=tz_dt)
    
    with pytest.raises(TypeError, match="Timezones are not supported"):
        age.set_times(end_time=tz_dt)


def test_age_negative():
    """Age handles negative durations when start_time > end_time."""
    # Arrange
    start = dt.datetime(2021, 1, 1)
    end = dt.datetime(2020, 1, 1)
    
    # Act
    age = Age(start, end)
    
    # Assert
    assert age.days == -366.0, "Age should be -366 days (2020 was a leap year)"
    assert age.seconds == -31622400.0, "Age should be -31622400 seconds"
    assert age.hours < 0, "Age hours should be negative"
    assert age.minutes < 0, "Age minutes should be negative"
    assert age.weeks < 0, "Age weeks should be negative"


@pytest.mark.parametrize("prop, expected", [
    ("seconds", -31622400.0),
    ("minutes", -527040.0),
    ("hours", -8784.0),
    ("days", -366.0),
    ("weeks", pytest.approx(-52.285714, rel=1e-3)),
    ("months", pytest.approx(-12.02365, rel=1e-3)),
    ("years", pytest.approx(-1.00274, rel=1e-3)),
])
def test_age_negative_properties(prop, expected):
    """Age properties are negative when start_time > end_time."""
    # Arrange
    start = dt.datetime(2021, 1, 1)
    end = dt.datetime(2020, 1, 1)
    
    # Act
    age = Age(start, end)
    
    # Assert
    assert getattr(age, prop) == expected, f"Age {prop} should be {expected} for negative duration"


def test_age_smoke():
    """Smoke test for Age class instantiation and basic properties."""
    # Arrange
    start = dt.datetime(2023, 1, 1, 0, 0, 0)
    
    # Act & Assert: Test years_precise increments correctly for 1-20 years
    for years in range(1, 21):  # 1 to 20 years
        end = start.replace(year=start.year + years)
        
        # Test positive direction: start to end
        age_positive = Age(start, end)
        assert age_positive.years_precise == pytest.approx(years, rel=1e-6), f"Failed for {years} years (positive)"
        
        # Test negative direction: end to start
        age_negative = Age(end, start)
        assert age_negative.years_precise == pytest.approx(-years, rel=1e-6), f"Failed for {years} years (negative)"

