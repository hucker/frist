import datetime as dt
from typing import Any
import pytest

from frist._util import in_half_open

@pytest.mark.parametrize(
    ("start", "value", "end", "expected"),
    [
        # integers
        (1, 1, 2, True),
        (1, 2, 2, False),  # value == end -> excluded

        # floats (and int/float mixing)
        (0.0, 0.5, 1.0, True),
        (0, 1.0, 1.0, False),

        # dates
        (dt.date(2025, 1, 1), dt.date(2025, 1, 1), dt.date(2025, 1, 2), True),
        (dt.date(2025, 1, 1), dt.date(2025, 1, 2), dt.date(2025, 1, 2), False),

        # datetimes (time-of-day within same calendar window)
        (
            dt.datetime(2025, 1, 1, 0, 0),
            dt.datetime(2025, 1, 1, 12, 0),
            dt.datetime(2025, 1, 2, 0, 0),
            True,
        ),
        (
            dt.datetime(2025, 1, 1, 0, 0),
            dt.datetime(2025, 1, 2, 0, 0),
            dt.datetime(2025, 1, 2, 0, 0),
            False,
        ),

        # tuples (lexicographic ordering)
        ((2025, 1), (2025, 1), (2025, 2), True),
        ((2025, 1), (2025, 2), (2025, 2), False),
    ],

)
def test_in_half_open_various_types(start: Any, value: Any, end: Any, expected: bool) -> None:
    """Verify in_half_open works for ints, floats, date, datetime and tuple types."""
    assert in_half_open(start, value, end) is expected, (
        f"in_half_open failed for start={start!r}, value={value!r}, end={end!r}: expected {expected}"
    )


def _cal_from(target: dt.datetime, ref: dt.datetime):
    """Helper to create a Cal via Chrono for tests."""
    from frist import Chrono

    return Chrono(target_time=target, reference_time=ref).cal


@pytest.mark.parametrize("ref", [dt.datetime(2025, 1, 1, 12, 0, 0)])
def _explicit(dt_tuple: tuple[int, int, int, int, int, int, int]) -> dt.datetime:
    """Helper to construct a datetime with explicit microseconds tuple.

    Tuple layout: (year, month, day, hour, minute, second, microsecond)
    """
    y, mo, d, h, mi, s, us = dt_tuple
    return dt.datetime(y, mo, d, h, mi, s, us)


@pytest.mark.parametrize("ref", [dt.datetime(2025, 1, 1, 12, 0, 0)])
def test_cal_half_open_boundaries_explicit(ref: dt.datetime) -> None:
    """Explicit golden-value tests for half-open boundaries per unit.

    Each assertion uses hand-written datetime literals (microseconds included where
    necessary) so the test doesn't reimplement the production boundary logic.
    """
    r = ref

    # Minute tests
    minute_cases = [
        ((2025, 1, 1, 11, 59, 59, 999_999), False),
        ((2025, 1, 1, 12, 0, 0, 0), True),
        ((2025, 1, 1, 12, 0, 1, 0), True),
        ((2025, 1, 1, 12, 0, 59, 999_999), True),
        ((2025, 1, 1, 12, 1, 0, 0), False),
    ]
    for tup, expected in minute_cases:
        assert _cal_from(_explicit(tup), r).in_minutes(0) is expected

    # Hour tests
    hour_cases = [
        ((2025, 1, 1, 11, 59, 59, 999_999), False),
        ((2025, 1, 1, 12, 0, 0, 0), True),
        ((2025, 1, 1, 12, 1, 0, 0), True),
        ((2025, 1, 1, 12, 59, 59, 999_999), True),
        ((2025, 1, 1, 13, 0, 0, 0), False),
    ]
    for tup, expected in hour_cases:
        assert _cal_from(_explicit(tup), r).in_hours(0) is expected

    # Day tests
    day_cases = [
        ((2024, 12, 31, 23, 59, 59, 999_999), False),
        ((2025, 1, 1, 0, 0, 0, 0), True),
        ((2025, 1, 1, 1, 0, 0, 0), True),
        ((2025, 1, 1, 23, 59, 59, 999_999), True),
        ((2025, 1, 2, 0, 0, 0, 0), False),
    ]
    for tup, expected in day_cases:
        assert _cal_from(_explicit(tup), r).in_days(0) is expected

    # Week tests (computed by production code as: start = ref.date() - timedelta(days=ref.weekday()))
    # For ref 2025-01-01 (Wednesday, weekday()==2) the week starts 2024-12-30.
    week_cases = [
        ((2024, 12, 29, 23, 59, 59, 999_999), False),
        ((2024, 12, 30, 0, 0, 0, 0), True),
        ((2024, 12, 31, 0, 0, 0, 0), True),
        ((2025, 1, 5, 23, 59, 59, 999_999), True),
        ((2025, 1, 6, 0, 0, 0, 0), False),
    ]
    for tup, expected in week_cases:
        assert _cal_from(_explicit(tup), r).in_weeks(0) is expected

    # Month tests (January 2025)
    month_cases = [
        ((2024, 12, 31, 23, 59, 59, 999_999), False),
        ((2025, 1, 1, 0, 0, 0, 0), True),
        ((2025, 1, 6, 0, 0, 0, 0), True),
        ((2025, 1, 31, 23, 59, 59, 999_999), True),
        ((2025, 2, 1, 0, 0, 0, 0), False),
    ]
    for tup, expected in month_cases:
        assert _cal_from(_explicit(tup), r).in_months(0) is expected

    # Quarter tests (Q1 2025)
    quarter_cases = [
        ((2024, 12, 31, 23, 59, 59, 999_999), False),
        ((2025, 1, 1, 0, 0, 0, 0), True),
        ((2025, 1, 16, 0, 0, 0, 0), True),
        ((2025, 3, 31, 23, 59, 59, 999_999), True),
        ((2025, 4, 1, 0, 0, 0, 0), False),
    ]
    for tup, expected in quarter_cases:
        assert _cal_from(_explicit(tup), r).in_quarters(0) is expected

    # Year tests (2025)
    year_cases = [
        ((2024, 12, 31, 23, 59, 59, 999_999), False),
        ((2025, 1, 1, 0, 0, 0, 0), True),
        ((2025, 1, 31, 0, 0, 0, 0), True),
        ((2025, 12, 31, 23, 59, 59, 999_999), True),
        ((2026, 1, 1, 0, 0, 0, 0), False),
    ]
    for tup, expected in year_cases:
        assert _cal_from(_explicit(tup), r).in_years(0) is expected
