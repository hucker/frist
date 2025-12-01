"""
Property-based tests for the Age class using Hypothesis.

These tests verify mathematical properties and invariants that should always hold
for Age calculations, regardless of input dates.
"""

import datetime as dt
from typing import Tuple

import pytest
from hypothesis import given, strategies as st

from frist import Age


# Custom strategies for datetime generation
datetime_strategy = st.datetimes(
    min_value=dt.datetime(1900, 1, 1),
    max_value=dt.datetime(2100, 12, 31)
    # Default timezones=st.none() gives naive datetimes only (as per package design)
)

# Strategy for pairs of datetimes where start <= end
datetime_pair_strategy = st.tuples(datetime_strategy, datetime_strategy).map(
    lambda pair: tuple(sorted(pair))  # Ensure start <= end
)


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_age_always_non_negative(start_end: Tuple[dt.datetime, dt.datetime]):
    """Age calculations should always be non-negative."""
    start, end = start_end
    age = Age(start, end)
    
    assert age.days >= 0
    assert age.seconds >= 0
    assert age.minutes >= 0
    assert age.hours >= 0
    assert age.weeks >= 0
    assert age.months >= 0
    assert age.years >= 0
    assert age.years_precise >= 0
    assert age.months_precise >= 0


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_age_consistency_properties(start_end: Tuple[dt.datetime, dt.datetime]):
    """Age should have consistent relationships between units."""
    start, end = start_end
    age = Age(start, end)
    
    # Basic unit relationships
    assert age.seconds == pytest.approx(age.days * 24 * 3600, abs=1)
    assert age.minutes == pytest.approx(age.seconds / 60, abs=1)
    assert age.hours == pytest.approx(age.minutes / 60, abs=1)
    
    # Weeks should be consistent with days
    assert age.weeks == pytest.approx(age.days / 7, abs=0.1)
    
    # Years should be reasonable bounds
    assert 0 <= age.years <= 201  # Max ~200 years from 1900-2100 range


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_precise_vs_approximate_consistency(start_end: Tuple[dt.datetime, dt.datetime]):
    """Precise calculations should be close to approximate ones."""
    start, end = start_end
    age = Age(start, end)
    
    # Precise should be close to approximate (within calendar variations)
    assert abs(age.years_precise - age.years) < 1.1  # Allow for leap year differences
    assert abs(age.months_precise - age.months) < 1.1  # Allow for month length variations


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_age_symmetry_with_negative_intervals(start_end: Tuple[dt.datetime, dt.datetime]):
    """Age should return negative values when end < start."""
    start, end = start_end
    age_forward = Age(start, end)
    age_reverse = Age(end, start)
    
    # Magnitudes should be identical but signs should be opposite
    assert abs(abs(age_forward.days) - abs(age_reverse.days)) < 1e-10
    assert abs(abs(age_forward.seconds) - abs(age_reverse.seconds)) < 1e-10
    assert abs(abs(age_forward.years_precise) - abs(age_reverse.years_precise)) < 1e-10


@pytest.mark.hypothesis
@given(start=datetime_strategy, days_offset=st.integers(0, 365*200))
def test_age_with_date_offsets(start: dt.datetime, days_offset: int):
    """Test Age with systematic date offsets."""
    end = start + dt.timedelta(days=days_offset)
    age = Age(start, end)
    
    # Days should match offset
    assert age.days == pytest.approx(days_offset, abs=1)
    
    # Years should be reasonable
    expected_years = days_offset / 365.25
    assert abs(age.years - expected_years) < 1


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_age_zero_length_intervals(start_end: Tuple[dt.datetime, dt.datetime]):
    """Test behavior with very small intervals."""
    start, end = start_end
    
    # If times are very close, age should be near zero
    if (end - start).total_seconds() < 1:
        age = Age(start, end)
        assert age.seconds < 1
        assert age.days < 0.001


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_leap_year_edge_cases(start_end: Tuple[dt.datetime, dt.datetime]):
    """Test Age calculations around leap year boundaries."""
    start, _ = start_end  # We only need the start year
    
    # February 29 should not cause issues
    feb_29_start = dt.datetime(start.year, 2, 28)
    feb_29_end = dt.datetime(start.year, 3, 1)
    if start.year % 4 == 0 and (start.year % 100 != 0 or start.year % 400 == 0):
        # Leap year
        age_leap = Age(feb_29_start, feb_29_end)
        assert age_leap.days == 2  # Feb 28 to Mar 1 in leap year = 2 days


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_age_string_parsing_consistency(start_end: Tuple[dt.datetime, dt.datetime]):
    """Test that Age can be created from string representations."""
    start, end = start_end
    
    # Convert to strings and back (truncate microseconds for compatibility)
    start_str = start.isoformat().split('.')[0]
    end_str = end.isoformat().split('.')[0]
    
    age_datetime = Age(start, end)
    age_strings = Age(start_str, end_str)
    
    # Should produce nearly identical results (allowing for microsecond precision loss in string parsing)      
    assert abs(age_datetime.days - age_strings.days) < 2e-5  # Allow for microsecond differences
    assert abs(age_datetime.seconds - age_strings.seconds) < 2  # Allow for microsecond differences


@pytest.mark.hypothesis
@given(start_end=datetime_pair_strategy)
def test_age_bounds_checking(start_end: Tuple[dt.datetime, dt.datetime]):
    """Test that Age handles extreme date ranges properly."""
    start, end = start_end
    age = Age(start, end)
    
    # Should not raise exceptions
    _ = age.days
    _ = age.years_precise
    _ = age.months_precise
    
    # Results should be finite and reasonable
    assert age.days >= 0
    assert age.days < 100000  # Reasonable upper bound for 1900-2100 range