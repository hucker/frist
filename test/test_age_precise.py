import pytest
import datetime as dt
from frist._age import Age
from frist._constants import DAYS_PER_MONTH


@pytest.mark.parametrize(
    "start, end, expected",
    [
        # Same year, not leap
        (
            dt.datetime(2021, 1, 1),
            dt.datetime(2021, 7, 2),
            (dt.datetime(2021, 7, 2) - dt.datetime(2021, 1, 1)).days / 365,
        ),
        # Leap year, same year
        (
            dt.datetime(2020, 2, 1),
            dt.datetime(2020, 8, 1),
            (dt.datetime(2020, 8, 1) - dt.datetime(2020, 2, 1)).days / 366,
        ),
        # Across leap year
        (
            dt.datetime(2019, 7, 1),
            dt.datetime(2020, 7, 1),
            (
                (dt.datetime(2019, 12, 31, 23, 59, 59) - dt.datetime(2019, 7, 1)).days
                / 365
            )
            + ((dt.datetime(2020, 7, 1) - dt.datetime(2020, 1, 1)).days / 366),
        ),
        # Multiple years, includes leap
        # Edge: start/end same day
        (dt.datetime(2022, 5, 1), dt.datetime(2022, 5, 1), 0.0),
    ],
)
def test_years_precise(start: dt.datetime, end: dt.datetime, expected: float) -> None:
    """
    Test Age.years_precise for leap years, same year, multiple years, and edge cases.
    Args:
        start (dt.datetime): Start datetime
        end (dt.datetime): End datetime
        expected (float): Expected precise years
    """
    # Arrange
    age: Age = Age(start, end)
    # Act
    actual = age.years_precise
    # Assert
    assert pytest.approx(actual, 1e-6) == expected, ( # type: ignore
        f"years_precise: expected {expected}, got {actual}"
    )  # type: ignore


@pytest.mark.parametrize(
    "start, end, expected",
    [
        # 31-day month
        (dt.datetime(2023, 1, 1), dt.datetime(2023, 2, 1), 1.0),
        # 28-day month (non-leap Feb)
        (dt.datetime(2023, 2, 1), dt.datetime(2023, 3, 1), 1.0),
        # 29-day month (leap Feb)
        (dt.datetime(2020, 2, 1), dt.datetime(2020, 3, 1), 1.0),
        # Across months with different lengths (half-open interval)
        # Jan: 1 day out of 31, Feb: full month (28 days), Mar: not included
        (dt.datetime(2023, 1, 31), dt.datetime(2023, 3, 1), (1 / 31) + 1),
        # Edge: start/end same day
        (dt.datetime(2022, 5, 1), dt.datetime(2022, 5, 1), 0.0),
    ],
)
def test_months_precise(start: dt.datetime, end: dt.datetime, expected: float) -> None:
    """
    Test Age.months_precise for long/short months, leap years, and edge cases.
    Args:
        start (dt.datetime): Start datetime
        end (dt.datetime): End datetime
        expected (float): Expected precise months
    """
    # Arrange
    age: Age = Age(start, end)
    # Act
    actual = age.months_precise
    # Assert
    assert pytest.approx(actual, 1e-6) == expected, ( # type: ignore
        f"months_precise: expected {expected}, got {actual}"
    )  # type: ignore


def test_months_property_normalized_lengths_all_months() -> None:
    """
    This test is similar to the one above that treats all actual months as 1 month regardless of length,
    but in this case we use normalized month lengths using the Age.months property which is just number of
    days divided by 30.44.  Under this scheme there are 4 possible normalized month lengths corresponding to
    the actual month lengths of 28, 29, 30, and 31 days.  So this test calculates all the months over a
    fiver year periods and verifies that there are 4 distinct normalized month lengths matching the expected values.
    """
    # Arrange
    actual: set[float] = set()
    for year in range(2000, 2006):
        for month in range(1, 13):
            start: dt.datetime = dt.datetime(year, month, 1)
            end: dt.datetime = dt.datetime(
                year if month < 12 else year + 1, month + 1 if month < 12 else 1, 1
            )
            age: Age = Age(start, end)
            normalized = age.months
            actual.add(normalized)

    expected: set[float] = {
        28 / DAYS_PER_MONTH,
        29 / DAYS_PER_MONTH,
        30 / DAYS_PER_MONTH,
        31 / DAYS_PER_MONTH,
    }

    # This equality should work even with sets of floats since the rations are exactly the same
    assert expected == actual, (
        f"Expected normalized month lengths {expected}, got {actual}"
    )
    assert DAYS_PER_MONTH == 30.44, (
        f"DAYS_PER_MONTH should be 30.44, got {DAYS_PER_MONTH}"
    )


@pytest.mark.parametrize(
    "same_month_start, same_month_end",
    [
        # Same day, same time
        (dt.datetime(2023, 2, 1, 0, 0), dt.datetime(2023, 2, 1, 0, 0)),
        # Same day, different times
        (dt.datetime(2023, 2, 1, 0, 0), dt.datetime(2023, 2, 1, 12, 0)),
        # Start at beginning of month, end at end of month
        (dt.datetime(2023, 2, 1, 0, 0), dt.datetime(2023, 2, 28, 23, 59, 59)),
        # Start and end at arbitrary times within the month
        (dt.datetime(2023, 2, 10, 6, 0), dt.datetime(2023, 2, 20, 18, 0)),
        # Leap year February
        (dt.datetime(2020, 2, 1, 0, 0), dt.datetime(2020, 2, 29, 23, 59, 59)),
        # End at first of next month (should be < 1.0)
        (dt.datetime(2023, 2, 1, 0, 0), dt.datetime(2023, 2, 28, 0, 0)),
    ],
)
def test_months_precise_same_month(
    same_month_start: dt.datetime, same_month_end: dt.datetime
) -> None:
    """
    Test Age.months_precise for intervals where start and end are in the same month, including time portions and edge cases.
    """
    # Arrange
    age: Age = Age(same_month_start, same_month_end)
    # Act
    actual = age.months_precise
    # Compute expected value using the same logic as months_precise
    month_start: dt.datetime = dt.datetime(same_month_start.year, same_month_start.month, 1)
    if same_month_start.month == 12:
        next_month = 1
        next_year = same_month_start.year + 1
    else:
        next_month = same_month_start.month + 1
        next_year = same_month_start.year
    month_end: dt.datetime = dt.datetime(next_year, next_month, 1)
    total_seconds = (month_end - month_start).total_seconds()
    interval_seconds = (same_month_end - same_month_start).total_seconds()
    expected = interval_seconds / total_seconds if interval_seconds > 0 else 0.0
    # Assert
    assert pytest.approx(actual, 1e-6) == expected, ( # type: ignore
        f"months_precise (same month): expected {expected}, got {actual}"
    )  

def test_months_precise_start_equals_end() -> None:
    """
    Test months_precise returns 0.0 when start == end.
    """
    start: dt.datetime = dt.datetime(2023, 5, 1, 12, 0)
    end: dt.datetime = dt.datetime(2023, 5, 1, 12, 0)
    age: Age = Age(start, end)
    actual = age.months_precise
    assert actual == 0.0, (
        f"months_precise: expected 0.0 when start == end, got {actual}"
    )


def test_years_precise_same_year() -> None:
    """
    Test years_precise for start and end in the same year.
    """
    start: dt.datetime = dt.datetime(2022, 3, 1)
    end: dt.datetime = dt.datetime(2022, 10, 1)
    age: Age = Age(start, end)
    actual = age.years_precise
    days_in_year = (dt.datetime(2023, 1, 1) - dt.datetime(2022, 1, 1)).days
    expected = (end - start).days / days_in_year
    assert pytest.approx(actual, 1e-6) == expected, (  # type: ignore
        f"years_precise (same year): expected {expected}, got {actual}"
    )  


def test_months_precise_start_greater_than_end_raises() -> None:
    """
    Test months_precise raises ValueError when start > end.
    """
    start: dt.datetime = dt.datetime(2023, 6, 1)
    end: dt.datetime = dt.datetime(2023, 5, 1)
    age: Age = Age(start, end)
    with pytest.raises(ValueError, match="start_time must be before end_time"):
        _ = age.months_precise


def test_years_precise_start_greater_than_end_raises() -> None:
    """
    Test years_precise raises ValueError when start > end.
    """
    start: dt.datetime = dt.datetime(2024, 1, 1)
    end: dt.datetime = dt.datetime(2023, 1, 1)
    age: Age = Age(start, end)
    with pytest.raises(ValueError, match="start_time must be before end_time"):
        _ = age.years_precise


def test_next_month_year_rollover() -> None:
    """
    Arrange: Set year=2025, month=12
    Act: Call _next_month_year
    Assert: Should return (2026, 1)
    """
    actual = Age._next_month_year(2025, 12)
    expected = (2026, 1)
    assert actual == expected, f"_next_month_year: expected {expected}, got {actual}"


@pytest.mark.parametrize(
    "end_day,expected",
    [
        (8, 0.25),  # Feb 1 to Feb 8 (7 days, .25 of Feb)
        (15, 0.5),  # Feb 1 to Feb 15 (14 days, .5 of Feb)
        (22, 0.75),  # Feb 1 to Feb 22 (21 days, .75 of Feb)
    ],
)
def test_months_precise_february_non_leap(end_day: int, expected: float) -> None:
    """
    Arrange: Start date Feb 1, end date Feb <end_day> (2023, non-leap year)
    Act: Calculate months_precise
    Assert: Should match expected fraction of month
    """
    start: dt.datetime = dt.datetime(2023, 2, 1)
    end: dt.datetime = dt.datetime(2023, 2, end_day)
    age: Age = Age(start, end)
    actual = pytest.approx(age.months_precise, 0.01) # type: ignore

    assert actual == expected, (
        f"months_precise (Feb non-leap): expected {expected}, got {actual}"
    )
