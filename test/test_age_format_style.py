"""
Tests for the ``style`` argument of Age.format(): verbose (the default) versus compact.

Verbose prints the table's unit names with two decimals, exactly as before the argument
existed.  Compact prints the short labels in ``Age.COMPACT_LABELS`` with no decimals and no
space ("30h", "13d", "2mo"), and ``Age.parse`` reads every compact label back.
"""

import datetime as dt

import pytest

from frist import Age
from frist._constants import SECONDS_PER_MONTH


@pytest.mark.parametrize(
    "delta",
    [dt.timedelta(seconds=46), dt.timedelta(hours=30), dt.timedelta(days=20)],
)
def test_default_style_is_verbose(delta: dt.timedelta) -> None:
    """format() without style is identical to style='verbose', so existing callers see no change."""
    # Arrange
    age = Age.from_timedelta(delta)
    # Act
    actual = age.format()
    expected = age.format(style="verbose")
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


@pytest.mark.parametrize(
    "delta, expected",
    [
        (dt.timedelta(seconds=46), "46s"),
        (dt.timedelta(minutes=90), "90m"),
        (dt.timedelta(hours=30), "30h"),
        (dt.timedelta(hours=47.6), "48h"),
        (dt.timedelta(days=13), "13d"),
        (dt.timedelta(days=56), "8w"),
        (dt.timedelta(days=61), "2mo"),
        (dt.timedelta(days=731), "2y"),
        (dt.timedelta(hours=-47), "-47h"),
    ],
)
def test_compact_style_uses_short_labels(delta: dt.timedelta, expected: str) -> None:
    """Compact output is the rounded value and the short label, with no space."""
    # Arrange
    age = Age.from_timedelta(delta)
    # Act
    actual = age.format(style="compact")
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0.0005, "500us"),
        (0.08, "80ms"),
        (46.0, "46s"),
        (90.0, "2m"),
        (20 * 3600.0, "20h"),
        (40 * 86400.0, "40d"),
    ],
)
def test_compact_style_with_duration_units(seconds: float, expected: str) -> None:
    """Compact labels apply to any table, including the sub-second rows of DURATION_UNITS."""
    # Act
    actual = Age.from_seconds(seconds).format(units=Age.DURATION_UNITS, style="compact")
    # Assert
    assert actual == expected, f"Expected '{expected}', got '{actual}'"


def test_compact_style_keeps_an_explicit_fmt() -> None:
    """A caller's fmt wins; compact only swaps the labels."""
    # Act
    actual = Age.from_seconds(46).format(style="compact", fmt="{value:.1f} {unit}")
    # Assert
    assert actual == "46.0 s", f"Expected '46.0 s', got '{actual}'"


def test_verbose_style_keeps_an_explicit_fmt() -> None:
    """The fmt argument behaves as before: full names, caller's number format."""
    # Act
    actual = Age.from_seconds(30 * 3600).format(fmt="{value:.0f} {unit}")
    # Assert
    assert actual == "30 hours", f"Expected '30 hours', got '{actual}'"


def test_compact_style_respects_now() -> None:
    """The now threshold applies before any formatting, in either style."""
    # Act
    actual = Age.from_seconds(5).format(style="compact", now=10)
    # Assert
    assert actual == "now", f"Expected 'now', got '{actual}'"


def test_unknown_style_is_rejected() -> None:
    """A typo in style raises with the accepted values named."""
    # Act / Assert
    with pytest.raises(ValueError, match="unknown style 'terse'; use 'verbose' or 'compact'"):
        Age.from_seconds(5).format(style="terse")


def test_every_compact_label_parses_back() -> None:
    """Age.parse accepts each compact label, so compact output round-trips."""
    # Arrange
    expected_units = {"microseconds", "milliseconds", "seconds", "minutes", "hours"}
    expected_units |= {"days", "weeks", "months", "years"}
    assert set(Age.COMPACT_LABELS) == expected_units, "every table unit needs a compact label"
    # Act / Assert
    for label in Age.COMPACT_LABELS.values():
        actual_seconds = Age.parse(f"2{label}")
        assert actual_seconds > 0, f"parse should accept the compact label {label!r}"


def test_parse_reads_the_compact_month_label() -> None:
    """'mo' is months, the one compact label parse did not know before."""
    # Act
    actual_seconds = Age.parse("23mo")
    # Assert
    assert actual_seconds == 23 * SECONDS_PER_MONTH, "23mo should be 23 average months"


def test_compact_round_trip_within_rounding() -> None:
    """Compact output parsed back lands within the half-unit the integer format rounds away."""
    # Arrange
    seconds = 13.4 * 86400  # 13.4 days prints as "13d"
    # Act
    text = Age.from_seconds(seconds).format(style="compact")
    actual_seconds = Age.parse(text)
    # Assert
    assert text == "13d", f"Expected '13d', got '{text}'"
    assert abs(actual_seconds - seconds) <= 0.5 * 86400, "round trip should be within half a day"
