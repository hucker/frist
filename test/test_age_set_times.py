"""
Test Age.set_times for updating start_time with a fixed end_time, iterating over multiple start times.
"""
import datetime as dt
from frist import Age

def test_set_times_iterative_start_times() -> None:
    """
    Use case: Calculate ages for many start times with a known end_time.
    """
    end_time = dt.datetime(2024, 1, 5)
    start_times = [
        dt.datetime(2024, 1, 1),
        dt.datetime(2024, 1, 2),
        dt.datetime(2024, 1, 3),
        dt.datetime(2024, 1, 4),
    ]
    expected_days:list[float] = [4.0, 3.0, 2.0, 1.0]
    results:list[float]= []
    for st in start_times:
        age = Age(start_time=st, end_time=end_time)
        results.append(age.days)
    assert results == expected_days, f"Expected {expected_days}, got {results}"
