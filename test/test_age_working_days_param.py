"""
Parameterized edge case tests for Age.working_days with custom calendar policy.
Covers holidays, weekends, and weekdays over a 3-week span.
"""
import datetime as dt
import pytest
from frist import Age
from frist._cal_policy import CalendarPolicy

# Custom calendar: 3 weeks, holidays on Wed each week
HOLIDAYS = {
    "2024-01-03",  # Week 1 Wednesday
    "2024-01-10",  # Week 2 Wednesday
    "2024-01-17",  # Week 3 Wednesday
}
CAL_POLICY = CalendarPolicy(
    workdays=[0, 1, 2, 3, 4],  # Mon-Fri
    holidays=HOLIDAYS,
    start_of_business=dt.time(9, 0),
    end_of_business=dt.time(17, 0),
)

# Helper to create datetime
def make_dt(y: int, m: int, d: int, h: int = 0, mi: int = 0) -> dt.datetime:
    return dt.datetime(y, m, d, h, mi)

# Parameterized cases: (start, end, expected, description)
CASES = [
    # Single weekday, not holiday
    (make_dt(2024, 1, 2, 9), make_dt(2024, 1, 2, 17), 1.0, "Full weekday (Tue)"),
    # Single holiday
    (make_dt(2024, 1, 3, 9), make_dt(2024, 1, 3, 17), 0.0, "Full holiday (Wed)"),
    # Single weekend
    (make_dt(2024, 1, 6, 9), make_dt(2024, 1, 6, 17), 0.0, "Full weekend (Sat)"),
    # Weekday to holiday
    (make_dt(2024, 1, 2, 9), make_dt(2024, 1, 3, 17), 1.0, "Weekday to holiday (Tue-Wed)"),
    # Holiday to weekday
    (make_dt(2024, 1, 3, 9), make_dt(2024, 1, 4, 17), 1.0, "Holiday to weekday (Wed-Thu)"),
    # Weekend to weekday
    (make_dt(2024, 1, 6, 9), make_dt(2024, 1, 8, 17), 1.0, "Weekend to weekday (Sat-Mon)"),
    # Weekday to weekend
    (make_dt(2024, 1, 5, 9), make_dt(2024, 1, 6, 17), 1.0, "Weekday to weekend (Fri-Sat)"),
    # Span: weekday, holiday, weekend
    (make_dt(2024, 1, 2, 9), make_dt(2024, 1, 6, 17), 3.0, "Tue-Sat (Tue, Thu, Fri)"),
    # Span: weekend, holiday, weekday
    (make_dt(2024, 1, 6, 9), make_dt(2024, 1, 10, 17), 2.0, "Sat-Wed (Mon, Tue, Thu)"),
    # Span: all types
    (make_dt(2024, 1, 1, 9), make_dt(2024, 1, 17, 17), 10.0, "Full 3 weeks (all weekdays except holidays)"),
    # Partial business day
    (make_dt(2024, 1, 2, 13), make_dt(2024, 1, 2, 17), 0.5, "Half business day (Tue)"),
    # Start/end on holidays
    (make_dt(2024, 1, 3, 13), make_dt(2024, 1, 3, 17), 0.0, "Partial holiday (Wed)"),
    # Start/end on weekend
    (make_dt(2024, 1, 7, 13), make_dt(2024, 1, 7, 17), 0.0, "Partial weekend (Sun)"),
]

@pytest.mark.parametrize("start,end,expected,desc", CASES)
def test_working_days_param_cases(start: dt.datetime, end: dt.datetime, expected: float, desc: str) -> None:
    """AAA: Parameterized edge case test for Age.working_days with custom calendar policy."""
    age = Age(start, end, cal_policy=CAL_POLICY)
    result = age.working_days
    assert abs(result - expected) < 1e-6, f"{desc}: got {result}, expected {expected}"
