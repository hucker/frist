"""Tests for `Cal.second` unit behavior.

Focus: half-open window semantics, cross-minute boundaries, negative offsets,
empty windows validation, and boundary microsecond handling.

Style: AAA (Arrange-Act-Assert) with explicit expected/actual naming where helpful.
"""
import datetime as dt

import pytest

from frist import Cal


def test_cal_second_unit_val_and_boundary_in_():
    """Inside window is True; end-exclusive boundary is False; `val` is target second.

    - Arrange: reference aligned at whole second; choose inside and end-boundary targets.
    - Act: evaluate `second.in_(-2, 1)` and read `second.val`.
    - Assert: membership True/False and `val` equals expected.
    """
    # Arrange
    ref = dt.datetime(2025, 12, 5, 12, 0, 10, 0)
    target_inside = dt.datetime(2025, 12, 5, 12, 0, 9, 500000)
    target_at_end = dt.datetime(2025, 12, 5, 12, 0, 11, 0)

    # Act
    cal_inside = Cal(target_inside, ref)
    actual_inside = cal_inside.second.in_(-2, 1)
    cal_at_end = Cal(target_at_end, ref)
    actual_at_end = cal_at_end.second.in_(-2, 1)
    actual_val = cal_inside.second.val

    # Assert
    assert actual_inside is True
    assert actual_at_end is False
    assert actual_val == 9


def test_cal_second_unit_window_around_ref():
    """Window [-1, 1) includes ref second and prior; excludes next second.

    - Arrange: reference with microseconds; construct boundary targets.
    - Act/Assert: evaluate membership around the ref second.
    """
    ref = dt.datetime(2025, 12, 5, 12, 0, 30, 123456)
    # Window [-1, 1) includes second 29 and 30; excludes 31
    actual_29 = Cal(dt.datetime(2025, 12, 5, 12, 0, 29, 999999), ref).second.in_(-1, 1)
    actual_30 = Cal(dt.datetime(2025, 12, 5, 12, 0, 30, 0), ref).second.in_(-1, 1)
    actual_31 = Cal(dt.datetime(2025, 12, 5, 12, 0, 31, 0), ref).second.in_(-1, 1)
    assert actual_29 is True
    assert actual_30 is True
    assert actual_31 is False


def test_cal_second_unit_cross_minute_boundaries():
    """Windows crossing minute boundaries include 59/00/01 and exclude 02.

    - Arrange: reference near minute boundary.
    - Act/Assert: check membership across the boundary.
    """
    ref = dt.datetime(2025, 12, 5, 12, 1, 0, 750000)
    # Window [-2, 2) spans seconds 59 (prev minute), 0, 1; excludes 2
    actual_59 = Cal(dt.datetime(2025, 12, 5, 12, 0, 59, 0), ref).second.in_(-2, 2)
    actual_00 = Cal(dt.datetime(2025, 12, 5, 12, 1, 0, 999999), ref).second.in_(-2, 2)
    actual_01 = Cal(dt.datetime(2025, 12, 5, 12, 1, 1, 1), ref).second.in_(-2, 2)
    actual_02 = Cal(dt.datetime(2025, 12, 5, 12, 1, 2, 0), ref).second.in_(-2, 2)
    assert actual_59 is True
    assert actual_00 is True
    assert actual_01 is True
    assert actual_02 is False


def test_cal_second_unit_negative_offsets_before_ref():
    """Negative offsets form windows strictly before the reference second.

    - Arrange: reference; targets at -5..-2 seconds.
    - Act/Assert: membership True for 10..12; False for 13.
    """
    ref = dt.datetime(2025, 12, 5, 12, 10, 15, 123456)
    # Window [-5, -2) includes seconds 10, 11, 12; excludes 13
    actual_10 = Cal(dt.datetime(2025, 12, 5, 12, 10, 10, 0), ref).second.in_(-5, -2)
    actual_12 = Cal(dt.datetime(2025, 12, 5, 12, 10, 12, 999999), ref).second.in_(-5, -2)
    actual_13 = Cal(dt.datetime(2025, 12, 5, 12, 10, 13, 0), ref).second.in_(-5, -2)
    assert actual_10 is True
    assert actual_12 is True
    assert actual_13 is False


def test_cal_second_unit_empty_window_start_eq_end():
    """Empty windows (`start == end`) raise ValueError to enforce half-open semantics.

    - Arrange: three targets around the reference second.
    - Act/Assert: calling `in_(0, 0)` raises ValueError and includes bounds in message.
    """
    ref = dt.datetime(2025, 12, 5, 12, 0, 30, 0)
    # Empty window: start == end raises ValueError to enforce half-open semantics
    for target in (
        dt.datetime(2025, 12, 5, 12, 0, 30, 0),
        dt.datetime(2025, 12, 5, 12, 0, 29, 999999),
        dt.datetime(2025, 12, 5, 12, 0, 31, 0),
    ):
        with pytest.raises(ValueError) as exc:
            Cal(target, ref).second.in_(0, 0)
        assert "start=" in str(exc.value) and "end=" in str(exc.value)


def test_cal_second_unit_exact_boundaries_microseconds():
    """Start boundary inclusive; end boundary exclusive with microsecond handling.

    - Arrange: reference; targets at start, just-before-end, and end.
    - Act/Assert: confirm half-open behavior down to microseconds.
    """
    ref = dt.datetime(2025, 12, 5, 12, 5, 20, 500000)
    # Start inclusive: exactly at start second with microsecond 0 and 999999
    actual_start_0 = Cal(dt.datetime(2025, 12, 5, 12, 5, 18, 0), ref).second.in_(-2, 1)
    actual_start_999999 = Cal(dt.datetime(2025, 12, 5, 12, 5, 18, 999999), ref).second.in_(-2, 1)
    # End exclusive: exactly at end second should be False
    actual_end_0 = Cal(dt.datetime(2025, 12, 5, 12, 5, 21, 0), ref).second.in_(-2, 1)
    # Just before end boundary with microsecond 999999 is True
    actual_before_end_999999 = Cal(
        dt.datetime(2025, 12, 5, 12, 5, 20, 999999),
        ref,
    ).second.in_(-2, 1)

    # Assert
    assert actual_start_0 is True
    assert actual_start_999999 is True
    assert actual_end_0 is False
    assert actual_before_end_999999 is True
