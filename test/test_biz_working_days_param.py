"""Parameterized edge case tests for Biz.working_days and Biz.business_days.

Covers holidays, weekends, and weekdays over a 3-week span.
"""
import datetime as dt
import pytest
from typing import List, Tuple, Set

from frist import Biz, CalendarPolicy

# Custom calendar: 3 weeks, holidays on Wed each week
HOLIDAYS: Set[str] = {
    "2024-01-03",  # Week 1 Wednesday
    "2024-01-10",  # Week 2 Wednesday
    "2024-01-17",  # Week 3 Wednesday
}
CAL_POLICY: CalendarPolicy = CalendarPolicy(
    workdays=[0, 1, 2, 3, 4],  # Mon-Fri
    holidays=HOLIDAYS,
    start_of_business=dt.time(9, 0),
    end_of_business=dt.time(17, 0),
)

def make_dt(y: int, m: int, d: int, h: int = 0, mi: int = 0) -> dt.datetime:
    return dt.datetime(y, m, d, h, mi)

# Parameterized cases: (start, end, expected_working, expected_business, description)
CASES: List[Tuple[dt.datetime, dt.datetime, float, float, str]] = [
    (make_dt(2024, 1, 2, 9),  make_dt(2024, 1, 2, 17), 1.0, 1.0, "Full weekday (Tue)"),
    (make_dt(2024, 1, 3, 9),  make_dt(2024, 1, 3, 17), 1.0, 0.0, "Full holiday (Wed)"),
    (make_dt(2024, 1, 6, 9),  make_dt(2024, 1, 6, 17), 0.0, 0.0, "Full weekend (Sat)"),
    (make_dt(2024, 1, 2, 9),  make_dt(2024, 1, 3, 17), 2.0, 1.0, "Weekday to holiday (Tue-Wed)"),
    (make_dt(2024, 1, 3, 9),  make_dt(2024, 1, 4, 17), 2.0, 1.0, "Holiday to weekday (Wed-Thu)"),
    (make_dt(2024, 1, 6, 9),  make_dt(2024, 1, 8, 17), 1.0, 1.0, "Weekend to weekday (Sat-Mon)"),
    (make_dt(2024, 1, 5, 9),  make_dt(2024, 1, 6, 17), 1.0, 1.0, "Weekday to weekend (Fri-Sat)"),
    (make_dt(2024, 1, 2, 9),  make_dt(2024, 1, 6, 17), 4.0, 3.0, "Tue-Sat (Tue, Wed, Thu, Fri)"),
    (make_dt(2024, 1, 6, 9),  make_dt(2024, 1, 10, 17),3.0, 2.0, "Sat-Wed (Mon, Tue, Wed)"),
    (make_dt(2024, 1, 1, 9),  make_dt(2024, 1, 17, 17),13.0,10.0, "Full 3 weeks (all weekdays incl. holidays)"),
    (make_dt(2024, 1, 2, 13), make_dt(2024, 1, 2, 17), 0.5, 0.5, "Half business day (Tue)"),
    (make_dt(2024, 1, 3, 13), make_dt(2024, 1, 3, 17), 0.5, 0.0, "Partial holiday (Wed)"),
    (make_dt(2024, 1, 7, 13), make_dt(2024, 1, 7, 17), 0.0, 0.0, "Partial weekend (Sun)"),
]

@pytest.mark.parametrize("start,end,expected_working,expected_business,desc", CASES)
def test_working_and_business_days_param_cases(
    start: dt.datetime,
    end: dt.datetime,
    expected_working: float,
    expected_business: float,
    desc: str,
) -> None:
    """Parameterized edge cases for `Biz.working_days` and `Biz.business_days`.

    Arrange: use the `CAL_POLICY` with recurring mid-week holidays.
    Act: compute `working_days` and `business_days` for each (start, end) pair.
    Assert: the results equal the expected values.
    """

    # Arrange
    biz: Biz = Biz(start, end, policy=CAL_POLICY)

    # Act
    result_working: float = biz.working_days
    result_business: float = biz.business_days

    # Assert
    assert result_working == pytest.approx(expected_working, rel=1e-6), (
        f"{desc} (working): got {result_working}, expected {expected_working}"
    )
    assert result_business == pytest.approx(expected_business, rel=1e-6), (
        f"{desc} (business): got {result_business}, expected {expected_business}"
    )
