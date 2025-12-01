"""
Property-based tests for the Biz class using Hypothesis.

These tests verify mathematical properties and invariants that should always hold
for Biz business calendar calculations, regardless of input dates and policies.
"""

import datetime as dt
from typing import Tuple

import pytest
from hypothesis import given, strategies as st, settings

from frist import Biz
from frist._biz_policy import BizPolicy


# Custom strategies for datetime generation with smaller ranges for performance
datetime_strategy = st.datetimes(
    min_value=dt.datetime(2000, 1, 1),
    max_value=dt.datetime(2030, 12, 31)
    # Default timezones=st.none() gives naive datetimes only (as per package design)
)

# Strategy for pairs of datetimes where target and reference can be in any order
datetime_pair_strategy = st.tuples(datetime_strategy, datetime_strategy)

# Strategy for BizPolicy with different fiscal year start months
biz_policy_strategy = st.builds(
    BizPolicy,
    fiscal_year_start_month=st.integers(min_value=1, max_value=12)
)


@pytest.mark.hypothesis
@given(target_ref=st.tuples(datetime_strategy, datetime_strategy), policy=biz_policy_strategy)
def test_biz_construction_properties(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test that Biz objects are constructed correctly."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    assert biz.target_time == target_dt
    assert biz.ref_time == ref_dt
    assert biz.cal_policy == policy


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
@settings(deadline=1000)  # Allow up to 1 second for these calculations
def test_biz_business_days_calculation(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test business_days property calculation."""
    target_dt, ref_dt = target_ref

    # Ensure target is not after ref (as per Biz requirement)
    if target_dt > ref_dt:
        target_dt, ref_dt = ref_dt, target_dt

    biz = Biz(target_dt, ref_dt, policy)

    business_days = biz.business_days

    # Business days should be non-negative
    assert business_days >= 0

    # If target and ref are the same, business_days should be 0
    if target_dt == ref_dt:
        assert business_days == 0

    # Business days should be less than or equal to calendar days
    calendar_days = (ref_dt - target_dt).total_seconds() / (24 * 3600)
    assert business_days <= abs(calendar_days)


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
@settings(deadline=1000)  # Allow up to 1 second for these calculations
def test_biz_working_days_calculation(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test working_days property calculation."""
    target_dt, ref_dt = target_ref

    # Ensure target is not after ref (as per Biz requirement)
    if target_dt > ref_dt:
        target_dt, ref_dt = ref_dt, target_dt

    biz = Biz(target_dt, ref_dt, policy)

    working_days = biz.working_days

    # Working days should be non-negative
    assert working_days >= 0

    # If target and ref are the same, working_days should be 0
    if target_dt == ref_dt:
        assert working_days == 0


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
def test_biz_in_business_days_consistency(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test in_business_days method consistency."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    # Test single business day window
    for offset in range(-5, 6):
        result = biz.in_business_days(offset)
        # Result should be boolean
        assert isinstance(result, bool)

    # Test range windows (ensure start < end)
    for start in range(-3, 4):
        for end in range(start + 1, start + 4):
            result = biz.in_business_days(start, end)
            assert isinstance(result, bool)


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
def test_biz_in_working_days_consistency(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test in_working_days method consistency."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    # Test single working day window
    for offset in range(-5, 6):
        result = biz.in_working_days(offset)
        assert isinstance(result, bool)

    # Test range windows (ensure start < end)
    for start in range(-3, 4):
        for end in range(start + 1, start + 4):
            result = biz.in_working_days(start, end)
            assert isinstance(result, bool)


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
def test_biz_in_fiscal_quarters_consistency(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test in_fiscal_quarters method consistency."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    # Calculate fiscal quarter difference manually
    fy_start_month = policy.fiscal_year_start_month
    ref_fy = Biz.get_fiscal_year(ref_dt, fy_start_month)
    ref_fq = Biz.get_fiscal_quarter(ref_dt, fy_start_month)
    ref_idx = ref_fy * 4 + (ref_fq - 1)

    target_fy = Biz.get_fiscal_year(target_dt, fy_start_month)
    target_fq = Biz.get_fiscal_quarter(target_dt, fy_start_month)
    target_idx = target_fy * 4 + (target_fq - 1)

    quarter_diff = target_idx - ref_idx

    # Test fiscal quarter windows
    for offset in range(-4, 5):
        expected = offset <= quarter_diff < offset + 1
        assert biz.in_fiscal_quarters(offset) == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
def test_biz_in_fiscal_years_consistency(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test in_fiscal_years method consistency."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    fy_start_month = policy.fiscal_year_start_month
    ref_fy = Biz.get_fiscal_year(ref_dt, fy_start_month)
    target_fy = Biz.get_fiscal_year(target_dt, fy_start_month)

    year_diff = target_fy - ref_fy

    # Test fiscal year windows
    for offset in range(-5, 6):
        expected = offset <= year_diff < offset + 1
        assert biz.in_fiscal_years(offset) == expected


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
def test_biz_unit_namespace_consistency(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test that UnitNamespace properties delegate correctly to in_* methods."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    # Test that cached properties delegate to the correct methods
    assert biz.bday.in_(-1, 1) == biz.in_business_days(-1, 1)
    assert biz.wday.in_(0, 2) == biz.in_working_days(0, 2)
    assert biz.fqtr.in_(-1, 0) == biz.in_fiscal_quarters(-1, 0)
    assert biz.fyear.in_(-1, 1) == biz.in_fiscal_years(-1, 1)

    # Test call syntax
    assert biz.bday(-1, 1) == biz.in_business_days(-1, 1)
    assert biz.fyear(-1, 1) == biz.in_fiscal_years(-1, 1)


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
def test_biz_convenience_properties(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test convenience properties like is_business_this_day, etc."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    # Test business day properties
    assert biz.is_business_last_day == biz.bday.in_(-1)
    assert biz.is_business_this_day == biz.bday.in_(0)
    assert biz.is_business_next_day == biz.bday.in_(1)

    # Test working day properties
    assert biz.is_workday_last_day == biz.wday.in_(-1)
    assert biz.is_workday_this_day == biz.wday.in_(0)
    assert biz.is_workday_next_day == biz.wday.in_(1)

    # Test fiscal properties
    assert biz.is_last_fiscal_quarter == biz.fqtr.in_(-1)
    assert biz.is_this_fiscal_quarter == biz.fqtr.in_(0)
    assert biz.is_next_fiscal_quarter == biz.fqtr.in_(1)

    assert biz.is_last_fiscal_year == biz.fyear.in_(-1)
    assert biz.is_this_fiscal_year == biz.fyear.in_(0)
    assert biz.is_next_fiscal_year == biz.fyear.in_(1)


@pytest.mark.hypothesis
@given(dt_obj=datetime_strategy, fy_start_month=st.integers(min_value=1, max_value=12))
def test_biz_get_fiscal_year(dt_obj: dt.datetime, fy_start_month: int):
    """Test get_fiscal_year static method."""
    fiscal_year = Biz.get_fiscal_year(dt_obj, fy_start_month)

    # Fiscal year should be reasonable
    assert fiscal_year >= 1900
    assert fiscal_year <= 2100

    # If month >= fy_start_month, fiscal year should be calendar year
    if dt_obj.month >= fy_start_month:
        assert fiscal_year == dt_obj.year
    else:
        # Otherwise, it should be calendar year - 1
        assert fiscal_year == dt_obj.year - 1


@pytest.mark.hypothesis
@given(dt_obj=datetime_strategy, fy_start_month=st.integers(min_value=1, max_value=12))
def test_biz_get_fiscal_quarter(dt_obj: dt.datetime, fy_start_month: int):
    """Test get_fiscal_quarter static method."""
    fiscal_quarter = Biz.get_fiscal_quarter(dt_obj, fy_start_month)

    # Fiscal quarter should be 1-4
    assert 1 <= fiscal_quarter <= 4

    # Test specific cases
    if fy_start_month == 1:
        # Standard calendar quarters
        expected = ((dt_obj.month - 1) // 3) + 1
        assert fiscal_quarter == expected
    # Additional validation could be added for other fy_start_month values


@pytest.mark.hypothesis
@given(target_ref=datetime_pair_strategy, policy=biz_policy_strategy)
def test_biz_properties_consistency(target_ref: Tuple[dt.datetime, dt.datetime], policy: BizPolicy):
    """Test consistency between various Biz properties."""
    target_dt, ref_dt = target_ref
    biz = Biz(target_dt, ref_dt, policy)

    # is_business_day should be consistent with is_workday and holiday
    expected_business_day = biz.is_workday and not biz.holiday
    assert biz.is_business_day == expected_business_day

    # Fiscal year and quarter properties should match static methods
    assert biz.fiscal_year == Biz.get_fiscal_year(target_dt, policy.fiscal_year_start_month)
    assert biz.fiscal_quarter == Biz.get_fiscal_quarter(target_dt, policy.fiscal_year_start_month)