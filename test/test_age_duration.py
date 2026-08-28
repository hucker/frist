"""
Tests for Age duration support.

Covers the sub-second properties (``milliseconds`` / ``microseconds``), the bare-duration
constructors (``from_seconds`` / ``from_timedelta``), sub-second units in ``Age.parse``,
the public ``AGE_UNITS`` / ``DURATION_UNITS`` tables, and the ``now`` threshold in
``Age.format``.  Golden values are chosen to be checkable by eye (90 s is 1.5 minutes,
40 days stays 40 days, 80 ms is 80 ms).
"""

import datetime as dt

import pytest

from frist import Age

ANCHOR: dt.datetime = dt.datetime(2000, 1, 1)


# --- sub-second properties -----------------------------------------------------------


@pytest.mark.parametrize(
    "start, end, expected_ms, expected_us",
    [
        (dt.datetime(2023, 1, 1), dt.datetime(2023, 1, 1, 0, 0, 1), 1000.0, 1_000_000.0),
        (dt.datetime(2023, 1, 1), dt.datetime(2023, 1, 1, 0, 0, 0, 500_000), 500.0, 500_000.0),
        (dt.datetime(2023, 1, 1), dt.datetime(2023, 1, 1, 0, 0, 0, 250), 0.25, 250.0),
        (dt.datetime(2023, 1, 1, 0, 0, 1), dt.datetime(2023, 1, 1), -1000.0, -1_000_000.0),
    ],
)
def test_age_sub_second_properties(
    start: dt.datetime, end: dt.datetime, expected_ms: float, expected_us: float
) -> None:
    """milliseconds / microseconds scale seconds by 1e3 / 1e6 and keep the sign."""
    # Arrange
    age = Age(start, end)
    # Act
    actual_ms = age.milliseconds
    actual_us = age.microseconds
    # Assert
    assert actual_ms == pytest.approx(expected_ms), f"Expected {expected_ms} ms, got {actual_ms}"
    assert actual_us == pytest.approx(expected_us), f"Expected {expected_us} us, got {actual_us}"


# --- bare-duration constructors ------------------------------------------------------


@pytest.mark.parametrize(
    "seconds",
    [0.0, 0.08, 1.5, 90.0, -1.0, -0.25, 40 * 86400.0],
)
def test_age_from_seconds_round_trips(seconds: float) -> None:
    """from_seconds yields an Age whose seconds equals the input, including negatives."""
    # Act
    age = Age.from_seconds(seconds)
    # Assert
    assert age.seconds == pytest.approx(seconds), f"Expected {seconds} s, got {age.seconds}"
    assert age.start_time == ANCHOR, "from_seconds should anchor start_time at 2000-01-01"


def test_age_from_timedelta_matches_total_seconds() -> None:
    """from_timedelta preserves total_seconds and ends at anchor + delta."""
    # Arrange
    delta = dt.timedelta(days=1, hours=2, milliseconds=80)
    expected_seconds = 86400 + 7200 + 0.08
    # Act
    age = Age.from_timedelta(delta)
    # Assert
    assert age.seconds == pytest.approx(expected_seconds), (
        f"Expected {expected_seconds} s, got {age.seconds}"
    )
    assert age.end_time == ANCHOR + delta, "end_time should be anchor + delta"


def test_age_from_seconds_negative_avoids_epoch() -> None:
    """Age(0, -1) routes through fromtimestamp (fails on Windows); from_seconds(-1) must not."""
    # Act
    age = Age.from_seconds(-1)
    # Assert
    assert age.seconds == -1.0, "Negative duration should be preserved"
    assert age.end_time == dt.datetime(1999, 12, 31, 23, 59, 59), "end should precede anchor"


def test_age_from_seconds_is_symmetric() -> None:
    """from_seconds(x).seconds == -from_seconds(-x).seconds."""
    assert Age.from_seconds(5).seconds == -Age.from_seconds(-5).seconds, "Sign symmetry broken"


# --- parse: sub-second units ---------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected_seconds",
    [
        ("100ms", 0.1),
        ("100 ms", 0.1),
        ("1.5msec", 0.0015),
        ("2 millisecond", 0.002),
        ("250milliseconds", 0.25),
        ("250us", 0.00025),
        ("1 usec", 0.000001),
        ("3 microsecond", 0.000003),
        ("500 microseconds", 0.0005),
        ("-100ms", -0.1),
        ("100MS", 0.1),
    ],
)
def test_age_parse_sub_second_units(text: str, expected_seconds: float) -> None:
    """parse understands ms/msec/millisecond(s) and us/usec/microsecond(s)."""
    actual = Age.parse(text)
    assert actual == pytest.approx(expected_seconds), f"Expected {expected_seconds}, got {actual}"


def test_age_parse_bare_m_is_still_minutes() -> None:
    """Adding 'ms' must not change the existing meaning of a bare 'm' (minutes)."""
    assert Age.parse("5m") == 300.0, "'m' should still mean minutes"


# --- public unit tables --------------------------------------------------------------


def test_age_units_is_the_format_default() -> None:
    """format() with no units is identical to format(units=Age.AGE_UNITS)."""
    # Arrange
    age = Age(dt.datetime(2023, 1, 1), dt.datetime(2023, 1, 15))
    # Act
    actual_default = age.format()
    actual_explicit = age.format(units=Age.AGE_UNITS)
    # Assert
    assert actual_default == "14.00 days", f"Unexpected default output {actual_default}"
    assert actual_explicit == actual_default, "AGE_UNITS should reproduce the default table"


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0.0005, "500.00 microseconds"),
        (0.002, "2.00 milliseconds"),
        (0.08, "80.00 milliseconds"),
        (0.5, "500.00 milliseconds"),
        (1.0, "1.00 seconds"),
        (46.0, "46.00 seconds"),  # clock boundary: never "0.77 minutes"
        (59.9, "59.90 seconds"),
        (60.0, "1.00 minutes"),
        (90.0, "1.50 minutes"),
        (3600.0, "1.00 hours"),
        (3 * 3600.0, "3.00 hours"),
        (24 * 3600.0, "1.00 days"),
        (40 * 86400.0, "40.00 days"),  # unbounded final row: never falls through to years
        (400 * 86400.0, "400.00 days"),
        (-0.5, "-500.00 milliseconds"),
        (-90.0, "-1.50 minutes"),
    ],
)
def test_duration_units_use_clock_boundaries(seconds: float, expected: str) -> None:
    """DURATION_UNITS switches at 1000/1000/60/60/24 and stays in days forever."""
    actual = Age.from_seconds(seconds).format(units=Age.DURATION_UNITS)
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


def test_age_units_still_fall_through_to_years() -> None:
    """AGE_UNITS ends at months; anything past 11 months is reported in years."""
    # Arrange
    age = Age(dt.datetime(2020, 1, 1), dt.datetime(2023, 1, 1))
    # Act
    actual = age.format(units=Age.AGE_UNITS)
    # Assert
    assert actual == "3.00 years", f"Expected '3.00 years', got '{actual}'"


# --- format(now=...) -----------------------------------------------------------------


@pytest.mark.parametrize(
    "now, expected",
    [
        (10, "now"),  # int -> seconds
        (5.0, "now"),  # float -> seconds
        (3, "4.00 seconds"),  # threshold not reached
        ("10 s", "now"),  # string carries its own unit
        ("1.1 min", "now"),
        ("2s", "4.00 seconds"),
        (None, "4.00 seconds"),  # default: no threshold
    ],
)
def test_age_format_now_threshold(now: int | float | str | None, expected: str) -> None:
    """A number is seconds, a string is parsed with its own unit; below it -> now_text."""
    actual = Age.from_seconds(4).format(now=now)
    assert actual == expected, f"now={now!r}: expected '{expected}', got '{actual}'"


def test_age_format_now_text_and_sub_second_string() -> None:
    """A '100ms' threshold with custom now_text works alongside DURATION_UNITS."""
    # Arrange
    age = Age.from_seconds(0.05)
    # Act
    actual = age.format(units=Age.DURATION_UNITS, now="100ms", now_text="live")
    # Assert
    assert actual == "live", f"Expected 'live', got '{actual}'"


def test_age_format_now_uses_abs() -> None:
    """A slightly-future age (clock skew) is still 'now'; a clearly-future one is not."""
    assert Age.from_seconds(-0.05).format(now=0.1) == "now", "Small negative age should be now"
    assert Age.from_seconds(-5).format(now=0.1) == "-5.00 seconds", "Large negative age is not now"


def test_age_format_now_boundary_is_exclusive() -> None:
    """An age exactly equal to the threshold is formatted, not collapsed to now_text."""
    actual = Age.from_seconds(10).format(now=10)
    assert actual == "10.00 seconds", f"Expected '10.00 seconds', got '{actual}'"


def test_age_format_now_takes_precedence_over_units() -> None:
    """The now check runs before the unit table walk."""
    actual = Age.from_seconds(0.5).format(units=Age.DURATION_UNITS, now=1)
    assert actual == "now", f"Expected 'now', got '{actual}'"
