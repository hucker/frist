"""Tests for `Cal` shortcut properties (is_today, is_yesterday, is_tomorrow,
is_last_week/is_this_week/is_next_week, is_last_month/is_this_month/is_next_month,
is_last_quarter/is_this_quarter/is_next_quarter, is_last_year/is_this_year/is_next_year).

Each shortcut is a thin wrapper around an `in_*` method and should follow
half-open semantics. These tests exercise the five canonical boundary cases:
below-lower, on-lower, interior (above-lower), on-upper (exclusive), above-upper.
"""
from __future__ import annotations

import datetime as dt


from frist import Cal


def _check_five(prop: str, ref: dt.datetime, dt_below: dt.datetime, dt_on_lower: dt.datetime,
                dt_above_lower: dt.datetime, dt_on_upper: dt.datetime, dt_above_upper: dt.datetime) -> None:
    """Helper: assert five-case expectations for Cal(...).{prop} given `ref`.

    The helper calls `getattr(Cal(t, ref), prop)` for each datetime and asserts
    the expected boolean membership for the five positions.
    """
    def call(t: dt.datetime) -> bool:
        return getattr(Cal(t, ref), prop)

    assert call(dt_below) is False, f"{prop}: below-lower should be False ({dt_below})"
    assert call(dt_on_lower) is True, f"{prop}: on-lower should be True ({dt_on_lower})"
    assert call(dt_above_lower) is True, f"{prop}: above-lower (interior) should be True ({dt_above_lower})"
    assert call(dt_on_upper) is False, f"{prop}: on-upper should be False (exclusive) ({dt_on_upper})"
    assert call(dt_above_upper) is False, f"{prop}: above-upper should be False ({dt_above_upper})"
