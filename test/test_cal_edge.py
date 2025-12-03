# --- Edge, parameterized, and error handling tests moved from test_cal.py ---
import datetime as dt
import pytest
from frist import Cal, Chrono
from frist._cal import normalize_weekday


@pytest.mark.parametrize(
    "spec,expected",
    [
        # Full names
        ("monday", 0), ("tuesday", 1), ("wednesday", 2), ("thursday", 3),
        ("friday", 4), ("saturday", 5), ("sunday", 6),
        # 3-letter abbreviations
        ("mon", 0), ("tue", 1), ("wed", 2), ("thu", 3),
        ("fri", 4), ("sat", 5), ("sun", 6),
        # 2-letter abbreviations
        ("mo", 0), ("tu", 1), ("we", 2), ("th", 3),
        ("fr", 4), ("sa", 5), ("su", 6),
        # Pandas style
        ("w-mon", 0), ("w-tue", 1), ("w-wed", 2), ("w-thu", 3),
        ("w-fri", 4), ("w-sat", 5), ("w-sun", 6),
        # Case insensitivity
        ("MONDAY", 0), ("Mon", 0), ("W-SUN", 6), ("thU", 3),
    ]
)
def test_weekday_normalization(spec: str, expected: int) -> None:
    """Test normalize_weekday exhaustively for all supported formats.
    Args:
            spec: Weekday string specification.
            expected: Expected normalized weekday integer (0=Monday, ... 6=Sunday).
    Ensures normalization works for all valid formats and cases.
    """
    assert normalize_weekday(spec) == expected, f"{spec} should map to {expected}"


def test_weekday_normalization_errors() -> None:
    """Test error handling in weekday normalization.
    Ensures ValueError is raised for invalid weekday specs.
    """
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("invalid")
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("xyz")


def test_cal_edge_cases() -> None:
    """Test edge cases in calendar functionality.
    Checks behavior for zero-difference datetimes and all window types.
    """
    target_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 30, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 30, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.minute.in_(0), "Target should be in current minute window"
    assert cal.hour.in_(0), "Target should be in current hour window"
    assert cal.day.in_(0, 1), "Target should be in current day window"
    assert cal.month.in_(0, 1), "Target should be in current month window"
    assert cal.qtr.in_(0), "Target should be in current quarter window"
    assert cal.year.in_(0), "Target should be in current year window"
    assert cal.week.in_(0), "Target should be in current week window"


def test_cal_month_edge_cases() -> None:
    """Test month calculations across year boundaries.
    Ensures correct month window logic across year transitions.
    """
    target_time: dt.datetime = dt.datetime(2023, 12, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.month.in_(-1, 0), "Target should be last month"
    assert not cal.month.in_(0), "Target should not be this month"
    target_time: dt.datetime = dt.datetime(2022, 6, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.month.in_(-20, -18)
    assert not cal.month.in_(-12, 0)


def test_cal_quarter_edge_cases() -> None:
    """Test quarter calculations across year boundaries.
    Ensures correct quarter window logic across year transitions.
    """
    target_time: dt.datetime = dt.datetime(2023, 11, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 2, 15, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.qtr.in_(-1)
    assert not cal.qtr.in_(0)
    target_time: dt.datetime = dt.datetime(2024, 3, 31, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 4, 1, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.qtr.in_(-1), "Target should be previous quarter"
    assert not cal.qtr.in_(0), "Target should not be current quarter"


def test_cal_year_edge_cases() -> None:
    """Test year calculations.
    Ensures correct year window logic at year boundaries and for multi-year ranges.
    """
    target_time: dt.datetime = dt.datetime(2023, 12, 31, 23, 59, 59)
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 0, 0, 1)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.year.in_(-1), "Target should be last year"
    assert not cal.year.in_(0), "Target should not be this year"
    assert cal.year.in_(-2, 0), "Target should be in range 2 years ago through now"


def test_cal_minutes_edge_cases() -> None:
    """Test minute window edge cases.
    Ensures correct minute window logic at minute boundaries and for
    multi-minute ranges.
    """
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 29, 59)
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 30, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.minute.in_(-1), "Target should be previous minute"
    assert not cal.minute.in_(0), "Target should not be current minute"
    assert cal.minute.in_(-5, 0), "Target should be in range 5 minutes ago through now"


def test_cal_hours_edge_cases() -> None:
    """Test hour window edge cases.
    Ensures correct hour window logic at hour boundaries and for multi-hour ranges.
    """
    target_time: dt.datetime = dt.datetime(2024, 1, 1, 11, 59, 59)
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.hour.in_(-1), "Target should be previous hour"
    assert not cal.hour.in_(0), "Target should not be current hour"
    assert cal.hour.in_(-6, 0), "Target should be in range 6 hours ago through now"


def test_cal_future_windows() -> None:
    """Test calendar windows for future dates.
    Ensures Cal can handle future dates for all window types.
    """
    target_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.day.in_(1, 2), "Target should be tomorrow"
    assert cal.hour.in_(24), "Target should be 24 hours from now"
    assert cal.minute.in_(1440), "Target should be 1440 minutes from now"
    assert cal.week.in_(0, 1), "Target should be in range this week through next week"
    target_time: dt.datetime = dt.datetime(2024, 2, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.month.in_(1, 2), "Target should be next month"
    target_time: dt.datetime = dt.datetime(2024, 7, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.qtr.in_(2), "Target should be 2 quarters from now"
    target_time: dt.datetime = dt.datetime(2026, 1, 15, 12, 0, 0)
    reference_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)
    z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
    cal: Cal = z.cal
    assert cal.year.in_(2), "Target should be 2 years from now"


@pytest.mark.parametrize(
    "spec,expected",
    [
        # Full names
        ("monday", 0), ("tuesday", 1), ("wednesday", 2), ("thursday", 3),
        ("friday", 4), ("saturday", 5), ("sunday", 6),
        # 3-letter abbreviations
        ("mon", 0), ("tue", 1), ("wed", 2), ("thu", 3),
        ("fri", 4), ("sat", 5), ("sun", 6),
        # 2-letter abbreviations
        ("mo", 0), ("tu", 1), ("we", 2), ("th", 3),
        ("fr", 4), ("sa", 5), ("su", 6),
        # Pandas style
        ("w-mon", 0), ("w-tue", 1), ("w-wed", 2), ("w-thu", 3),
        ("w-fri", 4), ("w-sat", 5), ("w-sun", 6),
        # Case insensitivity
        ("MONDAY", 0), ("Mon", 0), ("W-SUN", 6), ("thU", 3),
    ]
)
def test_normalize_weekday_valid(spec: str, expected: int) -> None:
    assert normalize_weekday(spec) == expected, f"{spec} should map to {expected}"
    assert normalize_weekday(spec) == expected, f"{spec} should map to {expected}"


@pytest.mark.parametrize(
    "bad_spec",
    [
        "nonday", "w-xyz", "abc", "", "w-", "mond", "tues", "w-funday",
        "noday", "funday", "w-xday"
    ]
)
def test_normalize_weekday_invalid(bad_spec: str) -> None:
    with pytest.raises(ValueError):
        normalize_weekday(bad_spec)
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday(bad_spec)


def test_cal_timezone_not_supported():
    tz_dt = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Cal(tz_dt, dt.datetime(2025, 1, 1))
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Cal(dt.datetime(2025, 1, 1), tz_dt)


def test_normalize_weekday_error_with_detailed_message():
    with pytest.raises(ValueError) as excinfo:
        normalize_weekday("invalid_day")
    error_msg = str(excinfo.value)
    assert "Invalid day specification" in error_msg
    assert "Full:" in error_msg
    assert "3-letter:" in error_msg
    assert "2-letter:" in error_msg
    assert "Pandas:" in error_msg


def test_cal_type_checking_imports():
    import frist._cal as cal_module

    assert hasattr(cal_module, "Cal")
    assert hasattr(cal_module, "normalize_weekday")
    assert hasattr(cal_module, "TYPE_CHECKING")
    from typing import TYPE_CHECKING

    assert TYPE_CHECKING is False


def test_cal_init_invalid_target_type():
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal("not-a-date", dt.datetime.now())  # type: ignore


def test_cal_init_invalid_ref_type():
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal(dt.datetime.now(), "not-a-date")  # type: ignore


def test_in_months_edge_cases():
    target = dt.datetime(2024, 1, 15)
    ref = dt.datetime(2024, 1, 1)
    cal: Cal = Cal(target, ref)
    assert cal.month.in_(0, 1), "Target should be this month"
    assert not cal.month.in_(-1), "Target should not be last month"
    assert not cal.month.in_(1), "Target should not be next month"
    assert cal.month.in_(-12, 1), "Target not in rng last 12 months through this month"


"""
Edge case and parameterized tests for Cal and related calendar logic.
"""



# ...tests will be moved here...
