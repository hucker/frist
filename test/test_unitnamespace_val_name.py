"""
Tests for UnitNamespace val and name properties.

AAA Pattern:
- Arrange: Construct Cal/Biz with explicit target/ref datetimes.
- Act: Read val/name (and day where applicable) from namespaces.
- Assert: Compare expected vs actual with clear assertion messages.

Follows frist CODESTYLE.md:
- Module and function docstrings.
- AAA comments per test.
- Assertions include expected and actual values for clarity.
"""

# pyright: reportUnknownMemberType=false

import datetime as dt

import pytest

from frist import Cal


@pytest.fixture(scope="module")
def cal() -> Cal:
    """Shared Cal instance with a fixed target/ref for all tests."""
    target: dt.datetime = dt.datetime(2024, 7, 15, 12, 34, 56)
    ref: dt.datetime = dt.datetime(2024, 1, 1, 0, 0, 0)
    return Cal(target_dt=target, ref_dt=ref)


def test_minute_namespace_val(cal: Cal) -> None:
    """MinuteNamespace.val returns the minute component (0-59)."""
    # Arrange
    # Arrange handled by fixture `cal`

    # Act/Assert
    assert cal.minute.val == 34, f"Minute val mismatch: expected=34, actual={cal.minute.val}"


def test_hour_namespace_val(cal: Cal) -> None:
    """HourNamespace.val returns the hour component (0-23)."""
    # Arrange
    # Arrange handled by fixture `cal`

    # Act/Assert
    assert cal.hour.val == 12, f"Hour val mismatch: expected=12, actual={cal.hour.val}"


def test_day_namespace_val_and_name(cal: Cal) -> None:
    """DayNamespace.val is ISO weekday (1-7) and .name is localized weekday name."""
    # Arrange (Wednesday)
    # Arrange handled by fixture `cal`

    # Act/Assert
    expected_weekday = cal.target_dt.isoweekday()
    expected_name = cal.target_dt.strftime("%A")
    assert cal.day.val == expected_weekday, (
        f"Day val mismatch: expected={expected_weekday}, actual={cal.day.val}"
    )
    assert cal.day.name == expected_name, (
        f"Day name mismatch: expected={expected_name}, actual={cal.day.name}"
    )


def test_week_namespace_val_and_day(cal: Cal) -> None:
    """WeekNamespace.val is ISO week number and .day is ISO weekday (1-7)."""
    # Arrange
    # Monday; ISO week should be 3 for 2025
    # Arrange handled by fixture `cal`

    # Act/Assert
    expected_week = cal.target_dt.isocalendar().week
    expected_day = cal.target_dt.isoweekday()
    assert cal.week.val == expected_week, (
        f"Week val mismatch: expected={expected_week}, actual={cal.week.val}"
    )
    assert cal.week.day == expected_day, (
        f"Week day mismatch: expected={expected_day}, actual={cal.week.day}"
    )


def test_month_namespace_val_name_day(cal: Cal) -> None:
    """MonthNamespace.val is 1-12, .name is month name, .day is day of month."""
    # Arrange
    # Arrange handled by fixture `cal`

    # Act/Assert
    assert cal.month.val == 7, f"Month val mismatch: expected=7, actual={cal.month.val}"
    assert cal.month.name == "July", f"Month name mismatch: expected=July, actual={cal.month.name}"
    assert cal.month.day == 15, f"Month day mismatch: expected=15, actual={cal.month.day}"


def test_quarter_namespace_val_and_name(cal: Cal) -> None:
    """QuarterNamespace.val returns 1-4 and .name returns Q{val}."""
    # Arrange (July -> Q3)
    # Arrange handled by fixture `cal`

    # Act/Assert
    assert cal.qtr.val == 3, f"Quarter val mismatch: expected=3, actual={cal.qtr.val}"
    assert cal.qtr.name == "Q3", f"Quarter name mismatch: expected=Q3, actual={cal.qtr.name}"


def test_year_namespace_val_and_day(cal: Cal) -> None:
    """YearNamespace.val is the year and .day is day-of-year (1-366)."""
    # Arrange
    # Arrange handled by fixture `cal`

    # Act/Assert
    assert cal.year.val == 2024, f"Year val mismatch: expected=2024, actual={cal.year.val}"
    expected_doy = cal.target_dt.timetuple().tm_yday
    assert cal.year.day == expected_doy, (
        f"Year day-of-year mismatch: expected={expected_doy}, actual={cal.year.day}"
    )
