"""
Tests for Age elapsed time across DST transitions: instants versus wall-clock readings.

Timezone-aware datetimes, POSIX timestamps and ``now`` are instants, so Age reports true
elapsed time between them even across a DST change.  Naive datetimes are wall-clock
readings and keep wall-clock arithmetic.  The zone is America/New_York; its 2025
transitions are 2025-03-09 02:00 (clocks forward to 03:00) and 2025-11-02 02:00 (clocks
back to 01:00).
"""

import datetime as dt
import time
from zoneinfo import ZoneInfo

import pytest

from frist import Age, Chrono

NY = ZoneInfo("America/New_York")

# Fall back: 23:00 EDT on Nov 1 to 12:00 EST on Nov 2 is 13 wall-clock hours, 14 real hours.
FALL_START = dt.datetime(2025, 11, 1, 23, 0, tzinfo=NY)
FALL_END = dt.datetime(2025, 11, 2, 12, 0, tzinfo=NY)
# Spring forward: 01:30 EST to 03:30 EDT is 2 wall-clock hours, 1 real hour.
SPRING_START = dt.datetime(2025, 3, 9, 1, 30, tzinfo=NY)
SPRING_END = dt.datetime(2025, 3, 9, 3, 30, tzinfo=NY)


@pytest.mark.parametrize(
    "start, end, expected_hours",
    [
        (FALL_START, FALL_END, 14.0),
        (FALL_END, FALL_START, -14.0),
        (SPRING_START, SPRING_END, 1.0),
        (FALL_START.astimezone(dt.UTC), FALL_END.astimezone(dt.UTC), 14.0),
    ],
)
def test_aware_pair_reports_real_elapsed_hours(
    start: dt.datetime, end: dt.datetime, expected_hours: float
) -> None:
    """Aware endpoints are instants: hours counts real elapsed time, not wall-clock hours."""
    # Act
    actual_hours = Age(start, end).hours
    # Assert
    assert actual_hours == expected_hours, f"Expected {expected_hours} h, got {actual_hours}"


def test_aware_pair_formats_real_elapsed_time() -> None:
    """format() sees the same elapsed seconds as the properties."""
    # Act
    actual = Age(FALL_START, FALL_END).format()
    # Assert
    assert actual == "14.00 hours", f"Expected '14.00 hours', got '{actual}'"


def test_aware_fold_distinguishes_the_repeated_hour() -> None:
    """01:30 happens twice on fall-back day; fold=1 is the second one, an hour after the first."""
    # Arrange
    first = dt.datetime(2025, 11, 2, 1, 30, tzinfo=NY, fold=0)
    second = dt.datetime(2025, 11, 2, 1, 30, tzinfo=NY, fold=1)
    # Act
    actual_hours = Age(first, second).hours
    # Assert
    assert actual_hours == 1.0, f"Expected 1.0 h between the two 01:30s, got {actual_hours}"


def test_naive_pair_keeps_wall_clock_arithmetic() -> None:
    """The same wall-clock readings without a zone are 13 hours apart: the civil-time contract."""
    # Arrange
    start = FALL_START.replace(tzinfo=None)
    end = FALL_END.replace(tzinfo=None)
    # Act
    actual_hours = Age(start, end).hours
    # Assert
    assert actual_hours == 13.0, f"Expected 13.0 wall-clock hours, got {actual_hours}"


def test_timestamp_pair_reports_real_elapsed_hours() -> None:
    """POSIX timestamps are instants: 14 real hours stay 14 hours whatever the local zone does."""
    # Arrange
    start_ts = FALL_START.timestamp()
    end_ts = FALL_END.timestamp()
    # Act
    age = Age(start_ts, end_ts)
    # Assert
    assert age.hours == 14.0, f"Expected 14.0 h, got {age.hours}"
    assert age.start_time.tzinfo is None, "timestamps still normalize to naive local datetimes"
    assert age.seconds == end_ts - start_ts, "seconds should be the exact timestamp difference"


def test_timestamp_with_default_end_measures_to_now() -> None:
    """Age(ts) with no end is 'how long ago': the gap to now, as elapsed time."""
    # Arrange
    an_hour_ago = time.time() - 3600
    # Act
    actual_seconds = Age(an_hour_ago).seconds
    # Assert
    assert 3600 <= actual_seconds < 3605, f"Expected about 3600 s, got {actual_seconds}"


def test_aware_start_with_default_end_uses_now_in_the_same_zone() -> None:
    """An aware start no longer raises when end is omitted: now is taken in its zone."""
    # Arrange
    start = dt.datetime.now(tz=NY) - dt.timedelta(minutes=30)
    # Act
    age = Age(start)
    # Assert
    assert age.end_time.tzinfo is NY, "end_time should be now in the start's zone"
    assert 1800 <= age.seconds < 1805, f"Expected about 1800 s, got {age.seconds}"


def test_aware_calendar_fractions_match_the_wall_clock() -> None:
    """months_precise / years_precise are calendar fractions in the zone's wall clock."""
    # Arrange: Jan 15 to Mar 15 spans a month boundary and the spring-forward transition.
    aware = Age(dt.datetime(2025, 1, 15, tzinfo=NY), dt.datetime(2025, 3, 15, tzinfo=NY))
    naive = Age(dt.datetime(2025, 1, 15), dt.datetime(2025, 3, 15))
    # Act
    actual_months = aware.months_precise
    actual_years = aware.years_precise
    # Assert
    assert actual_months == naive.months_precise, "same wall clock, same months_precise"
    assert actual_years == naive.years_precise, "same wall clock, same years_precise"
    assert abs(actual_months - 2.0) < 1e-9, f"Jan 15 to Mar 15 is 2.0 months, got {actual_months}"


def test_chrono_with_aware_target_and_default_ref() -> None:
    """Chrono accepts an aware target with ref omitted; the window is judged in its zone."""
    # Arrange
    now_ny = dt.datetime.now(tz=NY)
    # Act
    chrono = Chrono(target_dt=now_ny)
    # Assert
    assert chrono.cal.ref_dt.tzinfo is NY, "the default ref should be now in the target's zone"
    assert chrono.cal.day.in_(-1, 2) is True, (
        "an aware 'now' should fall inside yesterday..tomorrow"
    )


def test_chrono_timestamp_target_measures_an_instant() -> None:
    """Chrono hands a timestamp target to Age as a number, so .age agrees with Age(ts, ts)."""
    # Arrange
    start_ts = FALL_START.timestamp()
    end_ts = FALL_END.timestamp()
    # Act
    chrono = Chrono(target_dt=start_ts, ref_dt=end_ts)
    # Assert
    assert chrono.age.hours == 14.0, f"Expected 14.0 h through Chrono, got {chrono.age.hours}"
    assert chrono.age.end_time == chrono.ref_dt, "Age and Cal/Biz must share the reference time"


def test_chrono_timestamp_target_with_default_ref_measures_to_now() -> None:
    """Chrono(target_dt=ts) keeps one shared 'now' and still measures elapsed time to it."""
    # Arrange
    an_hour_ago = time.time() - 3600
    # Act
    chrono = Chrono(target_dt=an_hour_ago)
    # Assert
    assert 3600 <= chrono.age.seconds < 3605, f"Expected about 3600 s, got {chrono.age.seconds}"
    assert chrono.age.end_time == chrono.ref_dt, "Age and Cal/Biz must share the reference time"


def test_chrono_timestamp_target_with_naive_ref_is_wall_clock() -> None:
    """A timestamp target with a naive datetime reference is a wall-clock pair, as in Age."""
    # Arrange
    start_ts = FALL_START.timestamp()
    naive_ref = FALL_END.replace(tzinfo=None)
    # Act
    chrono = Chrono(target_dt=start_ts, ref_dt=naive_ref)
    # Assert
    assert chrono.age.hours == Age(start_ts, naive_ref).hours, "Chrono must agree with Age"
    assert chrono.age.end_time == chrono.ref_dt, "Age and Cal/Biz must share the reference time"


def test_from_seconds_is_unaffected() -> None:
    """Bare durations keep exact arithmetic."""
    # Act
    actual_minutes = Age.from_seconds(90).minutes
    # Assert
    assert actual_minutes == 1.5, f"90 s is 1.5 minutes, got {actual_minutes}"
