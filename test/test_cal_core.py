"""
Core calendar window tests for Cal and Chrono.
"""

import datetime as dt
import pytest
from frist import Cal, Chrono
from frist._util import normalize_weekday


def test_simple_cal_day_windows() -> None:
	"""Test Cal: one day apart, check day windows.

	Ensures Cal correctly identifies yesterday, today, and other day windows.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
	reference_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)
	cal: Cal = Cal(target_time, reference_time)

	# Act
	# (no separate action beyond construction)

	# Assert
	assert cal.target_dt == target_time, "cal.target_dt should match target_time"
	assert cal.ref_dt == reference_time, "cal.ref_dt should match reference_time"
	assert cal.day.in_(-1, 0), "Target should be yesterday relative to reference"
	assert cal.day.in_(-1, 0), "Target should be in range yesterday through today"
	assert not cal.day.in_(0), "Target should not be today"
	assert not cal.day.in_(-2), "Target should not be two days ago"


def test_cal_with_chrono() -> None:
	"""Test Cal functionality using Chrono objects.

	Ensures Cal can be constructed from a Chrono and properties are correct.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
	reference_time: dt.datetime = dt.datetime(2024, 1, 1, 18, 0, 0)  # Same day, 6 hours later
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)

	# Act
	cal: Cal = z.cal

	# Assert
	assert isinstance(cal, Cal), "cal should be instance of Cal"
	assert cal.target_dt == target_time, "cal.target_dt should match target_time"
	assert cal.ref_dt == reference_time, "cal.ref_dt should match reference_time"


def test_cal_in_minutes() -> None:
	"""Test calendar minute window functionality.

	Checks minute-based window membership for Cal.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 30, 0)
	reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 35, 0)  # 5 minutes later
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.minute.in_(-5, 0), "Should be within last 5 minutes through now"
	assert not cal.minute.in_(1, 5), "Should not be within future minutes"
	assert cal.minute.in_(-10, 0), "Should be within broader range including target"


def test_cal_in_hours() -> None:
	"""Test calendar hour window functionality.

	Checks hour-based window membership for Cal.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2024, 1, 1, 10, 30, 0)
	reference_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 30, 0)  # 2 hours later
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.hour.in_(-2, 0), "Should be within last 2 hours through now"
	assert not cal.hour.in_(-1, 0), "Should not be within just last hour (too narrow)"
	assert cal.hour.in_(-3, 0), "Should be within broader range"


def test_cal_in_days() -> None:
	"""Test calendar day window functionality.

	Checks day-based window membership for Cal.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
	reference_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)  # Next day
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.day.in_(-1, 1), "Target should be in range yesterday through today"
	assert cal.day.in_(-1, 0), "Target should be just yesterday"
	assert not cal.day.in_(0), "Target should not be today (target was yesterday)"
	assert not cal.day.in_(-2, -1), "Target should not be two days ago only"


def test_cal_in_weeks() -> None:
	"""Test calendar week window functionality.

	Checks week-based window membership for Cal.
	"""
	# Arrange
	# Monday Jan 1, 2024
	target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)  # Monday
	reference_time: dt.datetime = dt.datetime(2024, 1, 8, 12, 0, 0)  # Next Monday
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.week.in_(-1, 0), "Target should be in range last week through this week"
	assert cal.week.in_(-1, 0), "Target should be just last week"
	assert not cal.week.in_(0), "Target should not be this week"


def test_cal_in_months() -> None:
	"""Test calendar month window functionality.

	Checks month-based window membership for Cal.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 15
	reference_time: dt.datetime = dt.datetime(2024, 2, 15, 12, 0, 0)  # February 15
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.month.in_(-1, 0), "Target should be in rng last month through this month"
	assert cal.month.in_(-1, 0), "Target should be just last month"
	assert not cal.month.in_(0), "Target should not be this month"


def test_cal_in_quarters() -> None:
	"""Test calendar quarter window functionality.

	Checks quarter-based window membership for Cal.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1 2024
	reference_time: dt.datetime = dt.datetime(2024, 4, 15, 12, 0, 0)  # Q2 2024
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.qtr.in_(-1, 0), "Target should be in range last qtr through this qtr"
	assert cal.qtr.in_(-1), "Target should be just last quarter (Q1)"
	assert not cal.qtr.in_(0), "Target should not be this quarter (Q2)"


def test_cal_in_years() -> None:
	"""Test calendar year window functionality.

	Checks year-based window membership for Cal.
	"""
	# Arrange
	target_time: dt.datetime = dt.datetime(2023, 6, 15, 12, 0, 0)  # 2023
	reference_time: dt.datetime = dt.datetime(2024, 6, 15, 12, 0, 0)  # 2024
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.year.in_(-1, 0), "Target should be in range last year through this year"
	assert cal.year.in_(-1), "Target should be just last year"
	assert not cal.year.in_(0), "Target should not be this year"


def test_cal_single_vs_range() -> None:
	"""Test single time unit vs range specifications.

	Ensures Cal handles both single and range window checks.
	"""
	target_time: dt.datetime = dt.datetime(2024, 1, 1, 12, 0, 0)
	reference_time: dt.datetime = dt.datetime(2024, 1, 2, 12, 0, 0)

	# Arrange
	z: Chrono = Chrono(target_time=target_time, reference_time=reference_time)
	cal: Cal = z.cal

	# Act
	# (membership checks below)

	# Assert
	assert cal.day.in_(-1, 0), "Target should be just yesterday"

	# Assert (range)
	assert cal.day.in_(-1, 0), "Target should be in range yesterday through today"
