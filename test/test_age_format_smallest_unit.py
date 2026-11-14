"""
Tests for the ``smallest_unit`` floor of Age.format().

Below one of the smallest displayed unit the output is "< 1 unit" (compact "<1u") instead
of a fraction, and the table rows below that unit are never used.  The default floor is
the table's first unit: seconds for PLURAL_UNITS and AGE_UNITS, microseconds for
DURATION_UNITS.
"""

import re

import pytest

from frist import Age, AgeFormatStyle


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0.0, "< 1 second"),
        (0.5, "< 1 second"),
        (0.999, "< 1 second"),
        (1.0, "1.00 seconds"),
        (1.5, "1.50 seconds"),
        (-0.5, "< 1 second"),
    ],
)
def test_default_floor_is_one_second(seconds: float, expected: str) -> None:
    """With the default table anything under a second reads "< 1 second"; one second is a value."""
    # Act
    actual = Age.from_seconds(seconds).format()
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


def test_default_floor_compact() -> None:
    """The compact floor uses the short label with no spaces."""
    # Act
    actual = Age.from_seconds(0.5).format(style=AgeFormatStyle.COMPACT)
    # Assert
    assert actual == "<1s", f"Expected '<1s', got '{actual}'"


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (30 * 60, "< 1 hour"),
        (59 * 60 + 59, "< 1 hour"),
        (3600, "1.00 hours"),
        (90 * 60, "1.50 hours"),
        (30 * 3600, "30.00 hours"),
        (3 * 86400, "3.00 days"),
        (-30 * 60, "< 1 hour"),
    ],
)
def test_smallest_unit_hours(seconds: float, expected: str) -> None:
    """smallest_unit='hours' floors at an hour and never prints minutes or seconds."""
    # Act
    actual = Age.from_seconds(seconds).format(smallest_unit="hours")
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


def test_smallest_unit_hours_compact() -> None:
    """The compact floor text uses the compact label of the chosen unit."""
    # Act
    actual = Age.from_seconds(30 * 60).format(smallest_unit="hours", style="compact")
    # Assert
    assert actual == "<1h", f"Expected '<1h', got '{actual}'"


@pytest.mark.parametrize(
    "smallest_unit, seconds, expected",
    [
        ("minutes", 30, "< 1 minute"),
        ("days", 20 * 3600, "< 1 day"),
        ("days", 36 * 3600, "1.50 days"),
        ("weeks", 6 * 86400, "< 1 week"),
        ("months", 20 * 86400, "< 1 month"),
        ("years", 300 * 86400, "< 1 year"),
    ],
)
def test_smallest_unit_singular_names(smallest_unit: str, seconds: float, expected: str) -> None:
    """Every table unit has a singular floor text."""
    # Act
    actual = Age.from_seconds(seconds).format(smallest_unit=smallest_unit)
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0.0000004, "< 1 microsecond"),
        (0.0005, "500.00 microseconds"),
        (0.08, "80.00 milliseconds"),
    ],
)
def test_duration_units_floor_is_microseconds(seconds: float, expected: str) -> None:
    """DURATION_UNITS keeps its sub-second rows: its default floor is one microsecond."""
    # Act
    actual = Age.from_seconds(seconds).format(units=Age.DURATION_UNITS)
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


def test_now_threshold_beats_the_floor() -> None:
    """An explicit now threshold is checked first, in either style."""
    # Act
    actual = Age.from_seconds(0.5).format(now=1)
    # Assert
    assert actual == "now", f"Expected 'now', got '{actual}'"


def test_unknown_smallest_unit_is_rejected() -> None:
    """A unit that is not in the table raises and names the table's units."""
    # Act / Assert
    expected_message = (
        "Invalid smallest_unit 'fortnights'. Valid: "
        "('seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'years')"
    )
    with pytest.raises(ValueError, match=re.escape(expected_message)):
        Age.from_seconds(5).format(smallest_unit="fortnights")


def test_custom_table_names_are_not_singularized() -> None:
    """A custom unit name that is not one of the standard names is used as given."""
    # Arrange
    units = [(60, "ticks", lambda age: age.seconds)]
    # Act
    actual = Age.from_seconds(0.5).format(units=units)
    # Assert
    assert actual == "< 1 ticks", f"Expected '< 1 ticks', got '{actual}'"
