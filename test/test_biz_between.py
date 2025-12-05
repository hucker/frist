"""
Tests for `.between(start, end, inclusive)` on business-day and working-day units.
Covers all inclusivity modes and single-unit (`end=None`) mapping.
"""

import datetime as dt

import pytest

from frist import Biz, BizPolicy
from frist.units._base import Inclusive


@pytest.fixture()
def policy_standard() -> BizPolicy:
    # Mon-Fri workdays; one holiday on Wednesday
    return BizPolicy(
        workdays=[0, 1, 2, 3, 4],
        holidays={"2025-01-15"},
        start_of_business=dt.time(9, 0),
        end_of_business=dt.time(17, 0),
        fiscal_year_start_month=1,
    )


@pytest.fixture()
def ref_dt() -> dt.datetime:
    # Reference Thursday
    return dt.datetime(2025, 1, 16, 12, 0)


@pytest.mark.parametrize("inclusive", ["both", "left", "right", "neither"])
def test_work_day_between_single_unit_mapping(
    policy_standard: BizPolicy, ref_dt: dt.datetime, inclusive: Inclusive
) -> None:
    # Target on Thursday (a workday). Single-unit mapping should become in_(start, start+1)
    target = dt.datetime(2025, 1, 16, 10, 0)
    b = Biz(target, ref_dt, policy_standard)

    # Map expected per inclusive to canonical in_ calls
    if inclusive == "both":
        # in_(0, 1)
        assert b.work_day.between(0, None, inclusive) == b.work_day.in_(0, 1)
    elif inclusive == "left":
        # in_(0, 1)
        assert b.work_day.between(0, None, inclusive) == b.work_day.in_(0, 1)
    elif inclusive == "right":
        # start shifted by +1, end+1 -> in_(1, 2)
        assert b.work_day.between(0, None, inclusive) == b.work_day.in_(1, 2)
    else:  # neither
        # single-unit with start shifted: in_(1, 2)
        assert b.work_day.between(0, None, inclusive) == b.work_day.in_(1, 2)


@pytest.mark.parametrize(
    "inclusive, expected",
    [
        ("both", True),    # 0..1 inclusive includes 0
        ("left", True),    # 0..1 left-inclusive includes 0
        ("right", False),  # strictly after start -> excludes 0
        ("neither", False) # excludes both boundaries -> excludes 0
    ],
)
def test_work_day_between_multi_day_span(
    policy_standard: BizPolicy, ref_dt: dt.datetime, inclusive: Inclusive, expected: bool
) -> None:
    # Target on Thursday; test window spanning start=0..end=1 relative to ref Thursday.
    target = dt.datetime(2025, 1, 16, 10, 0)
    b = Biz(target, ref_dt, policy_standard)
    if inclusive == "neither":
        with pytest.raises(ValueError):
            b.work_day.between(0, 1, inclusive)
    else:
        assert b.work_day.between(0, 1, inclusive) is expected


@pytest.mark.parametrize("inclusive", ["both", "left", "right", "neither"])
def test_biz_day_between_single_unit_mapping_observes_holiday(
    policy_standard: BizPolicy, ref_dt: dt.datetime, inclusive: Inclusive
) -> None:
    # Target on the holiday Wednesday -> not a business day
    target = dt.datetime(2025, 1, 15, 10, 0)
    b = Biz(target, ref_dt, policy_standard)

    # For business day, membership should reflect holiday exclusion
    # Single-unit mapping expectations still hold, but results differ because target is a holiday
    if inclusive in {"both", "left"}:
        assert b.biz_day.between(0, None, inclusive) == b.biz_day.in_(0, 1)
    elif inclusive == "right":
        assert b.biz_day.between(0, None, inclusive) == b.biz_day.in_(1, 2)
    else:  # neither
        assert b.biz_day.between(0, None, inclusive) == b.biz_day.in_(1, 2)


@pytest.mark.parametrize(
    "target_day_offset, expected_biz, expected_work",
    [
        (-1, False, False),  # Not same day as ref
        (0, True, True),     # Same day as ref (Thu)
        (1, False, False),   # Not same day as ref
    ],
)
def test_between_alignment_consistency(
    policy_standard: BizPolicy,
    ref_dt: dt.datetime,
    target_day_offset: int,
    expected_biz: bool,
    expected_work: bool,
) -> None:
    # Exercise between vs in_ consistency across offsets
    base = ref_dt
    target = base + dt.timedelta(days=target_day_offset)
    b = Biz(target, ref_dt, policy_standard)

    # Use inclusive="left" to mirror core half-open semantics
    assert b.biz_day.between(0, None, "left") == b.biz_day.in_(0, 1)
    assert b.work_day.between(0, None, "left") == b.work_day.in_(0, 1)

    # And verify actual membership expectations for clarity
    assert (b.biz_day.in_(0)) is expected_biz
    assert (b.work_day.in_(0)) is expected_work
