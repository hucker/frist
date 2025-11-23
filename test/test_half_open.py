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
def test_cal_half_open_boundaries(ref: dt.datetime) -> None:
    """Verify Cal `in_*` methods observe half-open boundaries.

    For each scale we test three points:
      - inside the current unit (should be True)
      - exactly at the start of the next unit (should be False for current, True for next)
      - outside both (far future/past -> False)
    """

    # Minute boundary
    ref_dt = ref
    start_min = ref_dt.replace(second=0, microsecond=0)
    value_start_min = start_min
    value_below_min = start_min - dt.timedelta(microseconds=1)
    value_above_lower_min = start_min + dt.timedelta(seconds=1)
    value_last_min = (start_min + dt.timedelta(minutes=1)) - dt.timedelta(microseconds=1)
    value_next_min = start_min + dt.timedelta(minutes=1)
    assert _cal_from(value_below_min, ref_dt).in_minutes(0) is False
    assert _cal_from(value_start_min, ref_dt).in_minutes(0) is True
    assert _cal_from(value_above_lower_min, ref_dt).in_minutes(0) is True
    assert _cal_from(value_last_min, ref_dt).in_minutes(0) is True
    assert _cal_from(value_next_min, ref_dt).in_minutes(0) is False

    # Hour boundary
    start_hr = ref_dt.replace(minute=0, second=0, microsecond=0)
    value_start_hr = start_hr
    value_below_hr = start_hr - dt.timedelta(microseconds=1)
    value_above_lower_hr = start_hr + dt.timedelta(minutes=1)
    value_last_hr = (start_hr + dt.timedelta(hours=1)) - dt.timedelta(microseconds=1)
    value_next_hr = start_hr + dt.timedelta(hours=1)
    assert _cal_from(value_below_hr, ref_dt).in_hours(0) is False
    assert _cal_from(value_start_hr, ref_dt).in_hours(0) is True
    assert _cal_from(value_above_lower_hr, ref_dt).in_hours(0) is True
    assert _cal_from(value_last_hr, ref_dt).in_hours(0) is True
    assert _cal_from(value_next_hr, ref_dt).in_hours(0) is False

    # Day boundary
    start_day = ref_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    value_start_day = start_day
    value_below_day = start_day - dt.timedelta(microseconds=1)
    value_above_lower_day = start_day + dt.timedelta(hours=1)
    value_last_day = (start_day + dt.timedelta(days=1)) - dt.timedelta(microseconds=1)
    value_next_day = start_day + dt.timedelta(days=1)
    assert _cal_from(value_below_day, ref_dt).in_days(0) is False
    assert _cal_from(value_start_day, ref_dt).in_days(0) is True
    assert _cal_from(value_above_lower_day, ref_dt).in_days(0) is True
    assert _cal_from(value_last_day, ref_dt).in_days(0) is True
    assert _cal_from(value_next_day, ref_dt).in_days(0) is False

    # Week boundary (Monday start default) — pick a ref that is mid-week and test week transition
    # Use ref_dt above (2025-01-01) which is a Wednesday; compute the start of next week
    week_start = ref_dt.date() - dt.timedelta(days=(ref_dt.weekday()))
    start_of_next_week = week_start + dt.timedelta(weeks=1)
    start_week_dt = dt.datetime.combine(week_start, dt.time(0, 0))
    value_start_week = start_week_dt
    value_below_week = start_week_dt - dt.timedelta(microseconds=1)
    value_above_lower_week = start_week_dt + dt.timedelta(days=1)
    value_last_week = (start_week_dt + dt.timedelta(weeks=1)) - dt.timedelta(microseconds=1)
    value_next_week = dt.datetime.combine(start_of_next_week, dt.time(0, 0))
    assert _cal_from(value_below_week, ref_dt).in_weeks(0) is False
    assert _cal_from(value_start_week, ref_dt).in_weeks(0) is True
    assert _cal_from(value_above_lower_week, ref_dt).in_weeks(0) is True
    assert _cal_from(value_last_week, ref_dt).in_weeks(0) is True
    assert _cal_from(value_next_week, ref_dt).in_weeks(0) is False

    # Month boundary
    # compute next-month at midnight to avoid carrying ref's time component
    start_of_next_month = (ref_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_month = ref_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    value_start_month = start_month
    value_below_month = start_month - dt.timedelta(microseconds=1)
    # pick an interior date (above lower) — day 5 is safely inside month
    value_above_lower_month = start_month + dt.timedelta(days=5)
    # last instant of month: start of next month minus microsecond
    value_last_month = start_of_next_month - dt.timedelta(microseconds=1)
    value_next_month = start_of_next_month
    assert _cal_from(value_below_month, ref_dt).in_months(0) is False
    assert _cal_from(value_start_month, ref_dt).in_months(0) is True
    assert _cal_from(value_above_lower_month, ref_dt).in_months(0) is True
    assert _cal_from(value_last_month, ref_dt).in_months(0) is True
    assert _cal_from(value_next_month, ref_dt).in_months(0) is False

    # Quarter boundary: compute next quarter start
    cur_q = ((ref_dt.month - 1) // 3) + 1
    q_start_month = 3 * (cur_q - 1) + 1
    next_q_month = q_start_month + 3
    # normalize to midnight when computing quarter boundaries
    start_of_next_quarter = ref_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0).replace(month=((next_q_month - 1) % 12) + 1)
    # If month wrap occurred, adjust year
    if next_q_month > 12:
        start_of_next_quarter = start_of_next_quarter.replace(year=ref_dt.year + 1)
    # current quarter start
    cur_q_start_month = q_start_month
    cur_q_start = ref_dt.replace(month=cur_q_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    value_start_quarter = cur_q_start
    value_below_quarter = (cur_q_start - dt.timedelta(microseconds=1))
    # choose an interior quarter date: add 15 days
    value_above_lower_quarter = cur_q_start + dt.timedelta(days=15)
    value_last_quarter = start_of_next_quarter - dt.timedelta(microseconds=1)
    value_next_quarter = start_of_next_quarter
    assert _cal_from(value_below_quarter, ref_dt).in_quarters(0) is False
    assert _cal_from(value_start_quarter, ref_dt).in_quarters(0) is True
    assert _cal_from(value_above_lower_quarter, ref_dt).in_quarters(0) is True
    assert _cal_from(value_last_quarter, ref_dt).in_quarters(0) is True
    assert _cal_from(value_next_quarter, ref_dt).in_quarters(0) is False

    # Year boundary
    start_of_next_year = dt.datetime(ref_dt.year + 1, 1, 1, 0, 0, 0)
    start_year = dt.datetime(ref_dt.year, 1, 1, 0, 0, 0)
    value_start_year = start_year
    value_below_year = start_year - dt.timedelta(microseconds=1)
    value_above_lower_year = start_year + dt.timedelta(days=30)
    value_last_year = start_of_next_year - dt.timedelta(microseconds=1)
    value_next_year = start_of_next_year
    assert _cal_from(value_below_year, ref_dt).in_years(0) is False
    assert _cal_from(value_start_year, ref_dt).in_years(0) is True
    assert _cal_from(value_above_lower_year, ref_dt).in_years(0) is True
    assert _cal_from(value_last_year, ref_dt).in_years(0) is True
    assert _cal_from(value_next_year, ref_dt).in_years(0) is False
