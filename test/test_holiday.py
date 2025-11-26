"""
Holiday detection tests for Chrono/Cal.
"""
import datetime as dt

import pytest

from frist import Chrono,BizPolicy


@pytest.mark.parametrize(
    "holidays,target_time,expected",
    [
        ({'2025-12-25', '2025-01-01', '2025-07-04'}, dt.datetime(2025, 12, 25), True),
        ({'2025-12-25', '2025-01-01', '2025-07-04'}, dt.datetime(2025, 1, 1), True),
        ({'2025-12-25', '2025-01-01', '2025-07-04'}, dt.datetime(2025, 7, 4), True),
        ({'2025-12-25', '2025-01-01', '2025-07-04'}, dt.datetime(2024, 12, 25), False),
        ({'2025-12-25', '2025-01-01', '2025-07-04'}, dt.datetime(2026, 12, 25), False),
        ({'2025-12-25', '2025-01-01', '2025-07-04'}, dt.datetime(2025, 12, 24), False),
        ({'2025-12-25', '2025-01-01', '2025-07-04'}, dt.datetime(2025, 7, 5), False),
    ]
)
def test_holiday_detection_param(
    holidays: set[str], target_time: dt.datetime, expected: bool
):
    
    # Create BizPolicy with holiday overrides
    policy: BizPolicy = BizPolicy(holidays=holidays)

    chrono = Chrono(target_time=target_time, policy=policy)
    # Defensive: .date() only if target_time is datetime
    date_str:str = target_time.date().isoformat() if hasattr(target_time, "date") else str(target_time)
    holidays_list: list[str] = sorted(holidays)
   

    assert chrono.biz.holiday is expected, (
        f"Expected holiday={expected} for target_time={date_str} "
        f"with holidays={holidays_list}, got {chrono.biz.holiday}"
    )
