import datetime as dt
import pytest
from frist._cal_policy import BizPolicy

def make_policy():
    return BizPolicy(
        workdays=[0, 1, 2, 3, 4],
        start_of_business=dt.time(9, 0),
        end_of_business=dt.time(17, 0),
        holidays={"2025-11-13", "2025-12-25"},
    )

@pytest.mark.parametrize(
    "input_value,expected",
    [
        (5, True),  # Saturday
        (6, True),  # Sunday
        (0, False),  # Monday
        (dt.date(2025, 11, 15), True),  # Saturday
        (dt.date(2025, 11, 13), False),  # Thursday
        (dt.datetime(2025, 11, 16, 10, 0), True),  # Sunday
    ]
)
def test_is_weekend(input_value: int | dt.date | dt.datetime, expected: bool) -> None:
    """
    Test BizPolicy.is_weekend for various input types and values.
    """
    # Arrange
    policy = make_policy()
    # Act
    result = policy.is_weekend(input_value)
    # Assert
    assert result is expected, f"is_weekend({input_value!r}) expected {expected}, got {result}"

@pytest.mark.parametrize(
    "input_value,expected",
    [
        (0, True),  # Monday
        (5, False),  # Saturday
        (dt.date(2025, 11, 13), True),  # Thursday
        (dt.date(2025, 11, 15), False),  # Saturday
        (dt.datetime(2025, 11, 13, 10, 0), True),  # Thursday
        (dt.datetime(2025, 11, 15, 10, 0), False),  # Saturday
    ]
)
def test_is_workday(input_value: int | dt.date | dt.datetime, expected: bool) -> None:
    """
    Test BizPolicy.is_workday for various input types and values.
    """
    # Arrange
    policy = make_policy()
    # Act
    result = policy.is_workday(input_value)
    # Assert
    assert result is expected, f"is_workday({input_value!r}) expected {expected}, got {result}"

@pytest.mark.parametrize(
    "input_time,expected",
    [
        (dt.time(9, 0), True),
        (dt.time(16, 59), True),
        (dt.time(8, 59), False),
        (dt.time(17, 0), False),
        (dt.time(18, 0), False),
    ]
)
def test_is_business_time(input_time: dt.time, expected: bool) -> None:
    """
    Test BizPolicy.is_business_time for various time inputs.
    """
    # Arrange
    policy = make_policy()
    # Act
    result = policy.is_business_time(input_time)
    # Assert
    assert result is expected, f"is_business_time({input_time!r}) expected {expected}, got {result}"

@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("2025-11-13", True),
        (dt.date(2025, 12, 25), True),
        (dt.datetime(2025, 12, 25, 10, 0), True),
        ("2025-01-01", False),
        (dt.date(2025, 1, 1), False),
        (dt.datetime(2025, 1, 1, 0, 0), False),
    ]
)
def test_is_holiday(input_value: str | dt.date | dt.datetime, expected: bool) -> None:
    """
    Test BizPolicy.is_holiday for str, date, and datetime inputs.
    """
    # Arrange
    policy = make_policy()
    # Act
    result = policy.is_holiday(input_value)
    # Assert
    assert result is expected, f"is_holiday({input_value!r}) expected {expected}, got {result}"

def test_is_holiday_typeerror() -> None:
    """
    Test BizPolicy.is_holiday raises TypeError for invalid input types.
    """
    # Arrange
    policy = make_policy()
    # Act & Assert
    with pytest.raises(TypeError):
        policy.is_holiday(12345) #type: ignore # Intentional wrong type for test

@pytest.mark.parametrize(
    "dt_obj,expected",
    [
        # Holiday
        (dt.datetime(2025, 11, 13, 12, 0), 0.0),
        # Weekend
        (dt.datetime(2025, 11, 15, 12, 0), 0.0),
        # Before business hours
        (dt.datetime(2025, 11, 14, 8, 0), 0.0),
        # At start of business
        (dt.datetime(2025, 11, 14, 9, 0), 0.0),
        # During business hours (4 hours into business day)
        (dt.datetime(2025, 11, 14, 13, 0), 0.5),
        # At end of business
        (dt.datetime(2025, 11, 14, 17, 0), 1.0),
        # After business hours
        (dt.datetime(2025, 11, 14, 18, 0), 1.0),
    ]
)
def test_business_day_fraction(dt_obj: dt.datetime, expected: float) -> None:
    """
    Test BizPolicy.business_day_fraction for holidays, weekends, before/after business hours, and fractional calculation.
    """
    # Arrange
    policy = make_policy()
    # Act
    result = policy.business_day_fraction(dt_obj)
    # Assert
    if expected == 0.5:
        assert pytest.approx(result, 0.01) == expected, (           # type: ignore
            f"business_day_fraction({dt_obj!r}) expected approx {expected}, got {result}"
        )
    else:
        assert result == expected, (
            f"business_day_fraction({dt_obj!r}) expected {expected}, got {result}"
        )
