

# Frist

Frist is a property-based date and time utility for Python, designed to make relative date calculations and calendar logic simple and intuitive—without manual math. You create a Frist object with a target time (when something happened) and a reference time (usually "now").

Frist lets you answer questions like "Did this event happen today, this month, or this year?" using properties such as `in_day`, `in_month`, and `in_year`. These properties check if the target time lands anywhere in the current time unit window—even exactly at the start or end. You can also use ranges, like `in_days(-7, 0)` for "in the last 7 days" or `in_months(-1, 1)` for "from last month to next month." This is different from `.age.days`, which gives you the precise floating-point age in days between the target and reference times.

With Frist, you get instant answers to time-based questions with a single property, instead of writing complex date math. This makes it easy to work with calendar windows, fiscal periods, and custom time ranges.

---

**Note:** In German, "Frist" means "deadline" or "time limit." This reflects the package's focus on time windows, periods, and calendar logic.

## Key Concepts

- **Property-based API:** Most calculations are exposed as properties (e.g., `.age.days`, `.fiscal_year`, `.holiday`), not methods, so you rarely need to call functions or do arithmetic.
- **Minimal math required:** You can answer most date and calendar questions by accessing properties, not by writing formulas.
- **Flexible reference time:** Zeit lets you compare any target date/time to any reference date/time, not just "now".
- **Calendar and fiscal logic:** Built-in support for calendar windows (days, weeks, months, quarters, years) and fiscal year/quarter calculations.
- **Holiday detection:** Pass a set of holiday dates and instantly check if a date is a holiday.


## Quick Start

```python
import datetime as dt
from frist import Frist

# Create a Frist object for a target date
meeting = Frist(target_time=dt.datetime(2025, 12, 25))

# Check age properties
print(meeting.age.days)      # Days since meeting
print(meeting.age.hours)     # Hours since meeting

# Calendar windows
if meeting.cal.in_days(0):
  print("Meeting is today!")
if meeting.cal.in_weeks(-1):
  print("Meeting was last week.")

# Fiscal year and quarter
print(meeting.fiscal_year)      # Fiscal year for the meeting
print(meeting.fiscal_quarter)   # Fiscal quarter for the meeting

# Holiday detection
holidays = {'2025-12-25', '2025-01-01'}
meeting = Frist(target_time=dt.datetime(2025, 12, 25), holidays=holidays)
if meeting.holiday:
  print("This date is a holiday!")

# Compare to a custom reference time
project = Frist(target_time=dt.datetime(2025, 1, 1), reference_time=dt.datetime(2025, 2, 1))
print(project.age.days)  # Days between Jan 1 and Feb 1, 2025
```

## Features

## Time Scale Properties Table

| Time Scale    | Age Property         | Window Function(s)                    |
|-------------- |----------------------|---------------------------------------|
| Seconds       | `.age.seconds`       | `.cal.in_seconds(start, end)`         |
| Minutes       | `.age.minutes`       | `.cal.in_minutes(start, end)`         |
| Hours         | `.age.hours`         | `.cal.in_hours(start, end)`           |
| Days          | `.age.days`          | `.cal.in_days(start, end)`            |
| Weeks         | `.age.weeks`         | `.cal.in_weeks(start, end)`           |
| Months        | `.age.months`        | `.cal.in_months(start, end)`          |
| Quarters      | `.age.quarters`      | `.cal.in_quarters(start, end)`        |
| Years         | `.age.years`         | `.cal.in_years(start, end)`           |
| Fiscal Years  | `.age.fiscal_year`   | `.cal.in_fiscal_years(start, end)`    |
| Fiscal Qtrs   | `.age.fiscal_quarter`| `.cal.in_fiscal_quarters(start, end)` |

Each age property gives the precise floating-point difference in that unit. Each window function generates a boolean if the target time falls within the specified range of time units relative to the reference time.
Age properties (like `.age.days`) are designed for direct comparisons—use them to ask questions like `>`, `<`, `==`, or `!=` between the target and reference times. In contrast, the `in_*` window functions (like `.cal.in_days()`) return `True` or `False` depending on whether the target time falls within the specified range.
Note: The `end` parameter is optional. If omitted, the function checks for a single time unit (e.g., `.cal.in_days(0)` means "today").


## Fiscal Year & Quarter Example

Frist supports fiscal year and quarter calculations with customizable fiscal year start months. For example:

```python
# Fiscal year starts in April (fy_start_month=4)
meeting = Frist(target_time=dt.datetime(2025, 7, 15), fy_start_month=4)
print(meeting.fiscal_year)      # 2025 (fiscal year for July 15, 2025)
print(meeting.fiscal_quarter)   # 2 (Q2: July–September for April start)

# Check if a date is in a fiscal quarter or year window
if meeting.cal.in_fiscal_quarters(0):
  print("Meeting is in the current fiscal quarter.")
if meeting.cal.in_fiscal_years(0):
  print("Meeting is in the current fiscal year.")
```


## Holiday Detection Example

Frist can instantly check if a date is a holiday using a set of holiday dates:

```python
holidays = {
  '2025-12-25',  # Christmas
  '2025-01-01',  # New Year's Day
  '2025-07-04',  # Independence Day
}

# Check a specific date
meeting = Frist(target_time=dt.datetime(2025, 12, 25), holidays=holidays)
if meeting.holiday:
  print("Meeting date is a holiday!")

# Check multiple dates
for date_str in holidays:
  date = dt.datetime.strptime(date_str, '%Y-%m-%d')
  c = Frist(target_time=date, holidays=holidays)
  print(f"{date.date()}: Holiday? {c.holiday}")

# Use with custom reference time
project = Frist(target_time=dt.datetime(2025, 7, 4), reference_time=dt.datetime(2025, 7, 5), holidays=holidays)
if project.holiday:
  print("Project start date is a holiday!")
```

## Short Examples


### Age Calculation

```python
person = Frist(target_time=dt.datetime(1990, 5, 1), reference_time=dt.datetime(2025, 5, 1))
print(f"Age in days: {person.age.days}, Age in years: {person.age.years:.2f}")
```


### Calendar Windows

```python
meeting = Frist(target_time=dt.datetime(2025, 12, 25))
if meeting.cal.in_days(0):
  print("Meeting is today!")
if meeting.cal.in_weeks(-1):
  print("Meeting was last week.")
```

## API Reference


### Frist

`Frist(target_time: datetime, reference_time: datetime = None, fy_start_month: int = 1, holidays: set[str] = None)`

- **Properties:**
  - `age`: Age object with properties for `.days`, `.hours`, `.minutes`, `.seconds`, `.weeks`, `.months`, `.quarters`, `.years`, `.fiscal_year`, `.fiscal_quarter`.
  - `cal`: Cal object for calendar window logic.
  - `fiscal_year`: Fiscal year for the target time.
  - `fiscal_quarter`: Fiscal quarter for the target time.
  - `holiday`: True if target time is a holiday (if holidays set provided).

### Cal

`Cal(time_span: TimeSpan, fy_start_month: int = 1, holidays: set[str] = None)`

- **Properties:**
  - `dt_val`: Target datetime.
  - `base_time`: Reference datetime.
  - `fiscal_year`: Fiscal year for `dt_val`.
  - `fiscal_quarter`: Fiscal quarter for `dt_val`.
  - `holiday`: True if `dt_val` is a holiday.
  - `time_span`: The TimeSpan object.

- **Interval Methods:**
  - `in_minutes(start: int = 0, end: int | None = None) -> bool`
  - `in_hours(start: int = 0, end: int | None = None) -> bool`
  - `in_days(start: int = 0, end: int | None = None) -> bool`
  - `in_weeks(start: int = 0, end: int | None = None, week_start: str = "monday") -> bool`
  - `in_months(start: int = 0, end: int | None = None) -> bool`
  - `in_quarters(start: int = 0, end: int | None = None) -> bool`
  - `in_years(start: int = 0, end: int | None = None) -> bool`
  - `in_fiscal_quarters(start: int = 0, end: int | None = None) -> bool`
  - `in_fiscal_years(start: int = 0, end: int | None = None) -> bool`

- **Static Methods:**
  - `get_fiscal_year(dt: datetime, fy_start_month: int) -> int`
  - `get_fiscal_quarter(dt: datetime, fy_start_month: int) -> int`

- **Exceptions:**
  - All interval methods raise `ValueError` if `start > end`.
  - `normalize_weekday(day_spec: str) -> int` raises `ValueError` for invalid day specifications, with detailed error messages.

### Age

`Age(target_time: datetime, reference_time: datetime)`

- **Properties:**
  - `days`, `hours`, `minutes`, `seconds`, `weeks`, `months`, `quarters`, `years`, `fiscal_year`, `fiscal_quarter`

### TimeSpan (Protocol)

`TimeSpan`

- **Properties:**
  - `target_dt`: Target datetime.
  - `ref_dt`: Reference datetime.

---

## Testing and Support

[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/hucker/zeit/actions)
[![Ruff](https://img.shields.io/badge/ruff-100%25%20clean-brightgreen?logo=ruff&logoColor=white)](https://github.com/charliermarsh/ruff)
