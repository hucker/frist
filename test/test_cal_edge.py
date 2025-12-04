"""
Edge-case tests for Cal, focusing on boundaries and inclusive semantics.

Follows CODESTYLE: AAA comments and explicit expected/actual assertions.
"""

 
import datetime as dt

import pytest

from frist._cal import Cal
from frist._frist import Chrono
from frist._util import normalize_weekday


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
    # Arrange & Act
    actual = normalize_weekday(spec)
    # Assert
    assert actual == expected, f"normalize_weekday('{spec}') returned {actual}, expected {expected}"


def test_weekday_normalization_errors() -> None:
    """Test error handling in weekday normalization.
    Ensures ValueError is raised for invalid weekday specs.
    """
    # Arrange
    bad_specs = ["invalid", "xyz"]
    # Act & Assert
    for bad_spec in bad_specs:
        with pytest.raises(ValueError, match="Invalid day specification"):
            normalize_weekday(bad_spec)


def test_cal_edge_cases() -> None:
    """Test edge cases in calendar functionality.
    Checks behavior for zero-difference datetimes and all window types.
    """
    # Arrange
    target = dt.datetime(2024, 1, 15, 12, 30, 0)
    reference = dt.datetime(2024, 1, 15, 12, 30, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
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
    # Arrange
    target = dt.datetime(2023, 12, 15, 12, 0, 0)
    reference = dt.datetime(2024, 1, 15, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.month.in_(-1, 0), "Target should be last month"
    assert not cal.month.in_(0), "Target should not be this month"
    # Arrange for year transition
    target = dt.datetime(2022, 6, 15, 12, 0, 0)
    reference = dt.datetime(2024, 1, 15, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.month.in_(-20, -18), "Target should be in range -20 to -18 months"
    assert not cal.month.in_(-12, 0), "Target should not be in range -12 to 0 months"


def test_cal_quarter_edge_cases() -> None:
    """Test quarter calculations across year boundaries.
    Ensures correct quarter window logic across year transitions.
    """
    # Arrange
    target = dt.datetime(2023, 11, 15, 12, 0, 0)
    reference = dt.datetime(2024, 2, 15, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.qtr.in_(-1), "Target should be previous quarter"
    assert not cal.qtr.in_(0), "Target should not be current quarter"
    # Arrange for next test
    target = dt.datetime(2024, 3, 31, 12, 0, 0)
    reference = dt.datetime(2024, 4, 1, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.qtr.in_(-1), "Target should be previous quarter"
    assert not cal.qtr.in_(0), "Target should not be current quarter"


def test_cal_year_edge_cases() -> None:
    """Test year calculations.
    Ensures correct year window logic at year boundaries and for multi-year ranges.
    """
    # Arrange
    target = dt.datetime(2023, 12, 31, 23, 59, 59)
    reference = dt.datetime(2024, 1, 1, 0, 0, 1)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.year.in_(-1), "Target should be last year"
    assert not cal.year.in_(0), "Target should not be this year"
    assert cal.year.in_(-2, 0), "Target should be in range 2 years ago through now"


def test_cal_minutes_edge_cases() -> None:
    """Test minute window edge cases.
    Ensures correct minute window logic at minute boundaries and for
    multi-minute ranges.
    """
    # Arrange
    target = dt.datetime(2024, 1, 1, 12, 29, 59)
    reference = dt.datetime(2024, 1, 1, 12, 30, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.minute.in_(-1), "Target should be previous minute"
    assert not cal.minute.in_(0), "Target should not be current minute"
    assert cal.minute.in_(-5, 0), "Target should be in range 5 minutes ago through now"


def test_cal_hours_edge_cases() -> None:
    """Test hour window edge cases.
    Ensures correct hour window logic at hour boundaries and for multi-hour ranges.
    """
    # Arrange
    target = dt.datetime(2024, 1, 1, 11, 59, 59)
    reference = dt.datetime(2024, 1, 1, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.hour.in_(-1), "Target should be previous hour"
    assert not cal.hour.in_(0), "Target should not be current hour"
    assert cal.hour.in_(-6, 0), "Target should be in range 6 hours ago through now"


def test_cal_future_windows() -> None:
    """Test calendar windows for future dates.
    Ensures Cal can handle future dates for all window types.
    """
    # Arrange
    target = dt.datetime(2024, 1, 2, 12, 0, 0)
    reference = dt.datetime(2024, 1, 1, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    # Assert
    assert cal.day.in_(1, 2), "Target should be tomorrow"
    assert cal.hour.in_(24), "Target should be 24 hours from now"
    assert cal.minute.in_(1440), "Target should be 1440 minutes from now"
    assert cal.week.in_(0, 1), "Target should be in range this week through next week"
    # Arrange for next month
    target = dt.datetime(2024, 2, 15, 12, 0, 0)
    reference = dt.datetime(2024, 1, 15, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    assert cal.month.in_(1, 2), "Target should be next month"
    # Arrange for next quarter
    target = dt.datetime(2024, 7, 15, 12, 0, 0)
    reference = dt.datetime(2024, 1, 15, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    assert cal.qtr.in_(2), "Target should be 2 quarters from now"
    # Arrange for next year
    target = dt.datetime(2026, 1, 15, 12, 0, 0)
    reference = dt.datetime(2024, 1, 15, 12, 0, 0)
    chrono = Chrono(target_time=target, reference_time=reference)
    cal = chrono.cal
    assert cal.year.in_(2), "Target should be 2 years from now"


@pytest.mark.parametrize(
    "bad_spec",
    [
        "nonday", "w-xyz", "abc", "", "w-", "mond", "tues", "w-funday",
        "noday", "funday", "w-xday"
    ]
)
def test_normalize_weekday_invalid(bad_spec: str) -> None:
    # Arrange & Act & Assert
    with pytest.raises(ValueError):
        normalize_weekday(bad_spec)
    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday(bad_spec)


def test_cal_timezone_not_supported():
    # Arrange
    tz_dt = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    # Act & Assert
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Cal(tz_dt, dt.datetime(2025, 1, 1))
    with pytest.raises(TypeError, match="Timezones are not supported"):
        Cal(dt.datetime(2025, 1, 1), tz_dt)


def test_normalize_weekday_error_with_detailed_message():
    # Act
    with pytest.raises(ValueError) as excinfo:
        normalize_weekday("invalid_day")
    error_msg = str(excinfo.value)
    # Assert
    assert "Invalid day specification" in error_msg, (
        "Error message should mention 'Invalid day specification'"
    )
    assert "Full:" in error_msg, "Error message should mention 'Full:'"
    assert "3-letter:" in error_msg, "Error message should mention '3-letter:'"
    assert "2-letter:" in error_msg, "Error message should mention '2-letter:'"
    assert "Pandas:" in error_msg, "Error message should mention 'Pandas:'"


def test_cal_type_checking_imports():
    # Arrange
    import frist._cal as cal_module
    # Assert
    assert hasattr(cal_module, "Cal"), "_cal module should have 'Cal'"
    assert hasattr(cal_module, "TYPE_CHECKING"), "_cal module should have 'TYPE_CHECKING'"
    from typing import TYPE_CHECKING
    assert TYPE_CHECKING is False, "TYPE_CHECKING should be False at runtime"


def test_cal_init_invalid_target_type():
    # Act & Assert
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal("not-a-date", dt.datetime.now())  # type: ignore


def test_cal_init_invalid_ref_type():
    # Act & Assert
    with pytest.raises(TypeError, match="Unrecognized datetime string format"):
        Cal(dt.datetime.now(), "not-a-date")  # type: ignore


def test_in_months_edge_cases():
    # Arrange
    target = dt.datetime(2024, 1, 15)
    reference = dt.datetime(2024, 1, 1)
    cal = Cal(target, reference)
    # Assert
    assert cal.month.in_(0, 1), "Target should be this month"
    assert not cal.month.in_(-1), "Target should not be last month"
    assert not cal.month.in_(1), "Target should not be next month"
    assert cal.month.in_(-12, 1), "Target should be in range last 12 months through this month"


"""
Edge case and parameterized tests for Cal and related calendar logic.
"""



# ...tests will be moved here...
