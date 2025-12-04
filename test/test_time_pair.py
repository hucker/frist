"""
Test file for time_pair utility function.

Covers:
- time_pair with various input types
- error handling for invalid inputs
"""

import datetime as dt

import pytest

from frist._frist import time_pair


def test_time_pair_datetime() -> None:
    """Test time_pair with datetime objects."""
    # Arrange
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_tim, end_time=reference_tim)
    # Assert
    expected_target_tim = target_tim
    expected_reference_tim = reference_tim
    msg_target = f"Expected target {expected_target_tim}, got {actual_target_tim}"
    msg_reference = f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"
    assert actual_target_tim == expected_target_tim, msg_target
    assert actual_reference_tim == expected_reference_tim, msg_reference

def test_time_pair_date() -> None:
    """Test time_pair with date objects."""
    # Arrange
    target_dt: dt.date = dt.date(2024, 1, 1)
    reference_dt: dt.date = dt.date(2024, 1, 2)
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_dt, end_time=reference_dt)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1)
    expected_reference_tim = dt.datetime(2024, 1, 2)
    msg_target = f"Expected target {expected_target_tim}, got {actual_target_tim}"
    msg_reference = f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"
    assert actual_target_tim == expected_target_tim, msg_target
    assert actual_reference_tim == expected_reference_tim, msg_reference

def test_time_pair_float_timestamp() -> None:
    """Test time_pair with float timestamps."""
    # Arrange
    target_ts: float = dt.datetime(2024, 1, 1, 12, 0, 0).timestamp()
    reference_ts: float = dt.datetime(2024, 1, 2, 12, 0, 0).timestamp()
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_ts, end_time=reference_ts)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 12, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 12, 0, 0)
    msg_target = f"Expected target {expected_target_tim}, got {actual_target_tim}"
    msg_reference = f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"
    assert actual_target_tim == expected_target_tim, msg_target
    assert actual_reference_tim == expected_reference_tim, msg_reference

def test_time_pair_int_timestamp() -> None:
    """Test time_pair with int timestamps."""
    # Arrange
    target_ts: int = int(dt.datetime(2024, 1, 1, 12, 0, 0).timestamp())
    reference_ts: int = int(dt.datetime(2024, 1, 2, 12, 0, 0).timestamp())
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_ts, end_time=reference_ts)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 12, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 12, 0, 0)
    msg_target = f"Expected target {expected_target_tim}, got {actual_target_tim}"
    msg_reference = f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"
    assert actual_target_tim == expected_target_tim, msg_target
    assert actual_reference_tim == expected_reference_tim, msg_reference

def test_time_pair_string_datetime() -> None:
    """Test time_pair with string full datetime."""
    # Arrange
    start_str: str = "2024-01-01 12:00:00"
    end_str: str = "2024-01-02 12:00:00"
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=start_str, end_time=end_str)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 12, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 12, 0, 0)
    msg_target = f"Expected target {expected_target_tim}, got {actual_target_tim}"
    msg_reference = f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"
    assert actual_target_tim == expected_target_tim, msg_target
    assert actual_reference_tim == expected_reference_tim, msg_reference

def test_time_pair_string_date() -> None:
    """Test time_pair with string date only."""
    # Arrange
    start_str: str = "2024-01-01"
    end_str: str = "2024-01-02"
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=start_str, end_time=end_str)
    # Assert
    expected_target_tim = dt.datetime(2024, 1, 1, 0, 0, 0)
    expected_reference_tim = dt.datetime(2024, 1, 2, 0, 0, 0)
    msg_target = f"Expected target {expected_target_tim}, got {actual_target_tim}"
    msg_reference = f"Expected reference {expected_reference_tim}, got {actual_reference_tim}"
    assert actual_target_tim == expected_target_tim, msg_target
    assert actual_reference_tim == expected_reference_tim, msg_reference

def test_time_pair_end_time_none_defaults_to_now() -> None:
    """Test time_pair with end_time=None defaults to now."""
    # Arrange
    target_tim: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
    # Act
    actual_target_tim, actual_reference_tim = time_pair(start_time=target_tim, end_time=None)
    # Assert
    expected_target_tim = target_tim
    msg_target = f"Expected target {expected_target_tim}, got {actual_target_tim}"
    msg_reference = f"Expected reference to be datetime, got {type(actual_reference_tim)}"
    assert actual_target_tim == expected_target_tim, msg_target
    assert isinstance(actual_reference_tim, dt.datetime), msg_reference

def test_time_pair_start_time_none_raises() -> None:
    """Test time_pair with start_time=None raises TypeError."""
    # Arrange
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act & Assert
    with pytest.raises(TypeError):
        time_pair(start_time=None, end_time=reference_tim)

def test_time_pair_unsupported_type_raises() -> None:
    """Test time_pair with unsupported type raises TypeError."""
    # Arrange
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act & Assert
    with pytest.raises(TypeError):
        time_pair(start_time=[2024, 1, 1], end_time=reference_tim)

def test_time_pair_unsupported_string_format_raises() -> None:
    """Test time_pair with unsupported string format raises TypeError."""
    # Arrange
    reference_tim: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
    # Act & Assert
    with pytest.raises(TypeError):
        time_pair(start_time="not-a-date", end_time=reference_tim)
