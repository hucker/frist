"""
Test Age.set_times for updating start_time with a fixed end_time, iterating over multiple start times.
"""
import datetime as dt
import pytest
from frist import Age

def test_set_times_iterative_start_times() -> None:
    """
    AAA: Test updating start_time repeatedly with set_times, keeping end_time fixed.
    Use case: Calculate ages for many start times with a known end_time.
    """
    end_time = dt.datetime(2024, 1, 5)
    start_times = [
        dt.datetime(2024, 1, 1),
        dt.datetime(2024, 1, 2),
        dt.datetime(2024, 1, 3),
        dt.datetime(2024, 1, 4),
    ]
    expected_days = [4.0, 3.0, 2.0, 1.0]
    age = Age(start_time=start_times[0], end_time=end_time)
    results = []
    for st in start_times:
        age.set_times(start_time=st)
        results.append(age.days)
    assert results == expected_days, f"Expected {expected_days}, got {results}"
    # Also check that end_time remains unchanged
    assert age.end_time == end_time

# Optionally, print results for manual inspection
if __name__ == "__main__":
    end_time = dt.datetime(2024, 1, 1)
    start_times = [
        dt.datetime(2020, 1, 1),
        dt.datetime(2021, 1, 1),
        dt.datetime(2022, 1, 1),
        dt.datetime(2023, 1, 1),
    ]
    age = Age(start_time=start_times[0], end_time=end_time)
    for st in start_times:
        age.set_times(start_time=st)
        print(f"Start: {st.date()}  Years: {age.years}")
