# Frist: Unified Age and Calendar Logic

Frist is a modern Python library for property-based calendar, age, and time window calculations. Most operations are performed by accessing properties or calling simple methods—no manual math or low-level datetime manipulation required.

---

## Chrono: Age and Calendar in One Place

The `Chrono` class is the central interface for time-based logic in Frist. You provide a `target_time` (the date/time you want to analyze) and a `reference_time` (often just "now"). Chrono lets you ask both age-related and calendar window questions using simple properties and methods.

```text
Timeline and Window Boundaries for Half-Open Intervals

Suppose you want to know if your target date falls within a window around your reference date. Frist makes this easy:

  |-----------|------------|------------|------------|
  2024-05-06   2024-05-07   2024-05-08   2024-05-09   Date
   2DaysAgo     YesterDay     Target      Ref          Description
    -2           -1           0           +1         Window Index

With Chrono, you specify both dates and the window:

```python
from frist import Chrono
import datetime as dt

target = dt.datetime(2024, 5, 8)
reference = dt.datetime(2024, 5, 9)
chrono = Chrono(target_time=target, reference_time=reference)

print(chrono.cal.in_days(-1))   # True: target is 1 day before reference
print(chrono.cal.in_days(0))    # False: target is not the same day as reference
print(chrono.cal.in_days(-2, 0)) # True: target is in the window from 2 days ago up to reference
```

In the diagram above, the window for `in_days(-2, 0)` covers 2024-05-06, 2024-05-07, and 2024-05-08 (target), but not 2024-05-09 (reference). The API answers: is the target in the window? Yes or no.

This windowing works for any time scale—days, weeks, months, etc.—and always uses half-open intervals: the left boundary is inclusive, the right is exclusive.

print(chrono.cal.in_days(-1, 1))    # Is target within 1 day before/after reference?
```

```text

# Timeline and Window Boundaries for Half Open Intervals*
# Calendar Functions for in_day(start,end)
#
#       |-----------|------------|------------|------------|
#        2024-05-06   2024-05-07   2024-05-08   2024-05-09   Date
#         2DaysAgo     YesterDay     Today       Tomorrow    Description
#                       Target        Ref                    Var Names
#            -2           -1           0           +1        Start/End Indexes
#         
c = Chrono(target_date=may_05,ref_date=05)
print(c.in_days(-1))   #  True,  the target day is 1 day ago
print(c.in_Days(0))    #  False, the target time did not happen on day 0
print(c.in_days(-2,0)) #  True,  the target day is in the range
```

* What is a half open interval?  A half open inverval is used for setting up ranges along a number line.  By having one boundary <= and the other being ==, you are guarenteed that sequential window checks won't be true for the same value in sequential windows.  This has the side effect that if you ask for data in the range -1,0 it only returns data for 1 day ago

## Explicit Reference Time

You can always specify a custom reference time if you want to compare two specific dates:

```python
target = dt.datetime(2000, 1, 1)
reference = dt.datetime(2024, 1, 1)
chrono = Chrono(target_time=target, reference_time=reference)
print(chrono.age.years)   # Years between 2000 and 2024
# Example output: 24.0
print(chrono.cal.in_days(0))        # Is target the same day as reference?
# Example output: False
```

## Age and Cal Standalone

You can also use `Age` and `Cal` directly, but Chrono is recommended for unified logic:

```python
from frist import Age, Cal

age = Age(target_time=target, ref_time=reference)
print(age.years)  # Example output: 24.0
print(age.days)   # Example output: 8766

cal = Cal(target_dt=target, ref_dt=reference)
print(cal.in_days(0))      # Example output: False
print(cal.in_days(-2, 2))  # Example output: False
```

**Calendar Policy:**
The calendar object can calculate workdays, business hours, holidays, and more (details in a later section). By default, the policy is:

* Workdays: Monday–Friday
* Work hours: 9AM–5PM
* Holidays: none
  
This policy can easily be changed to fit your needs.

---

## Key Features

* **Property-based API:** Access date and time information through properties and high-level methods.
* **Calendar windows:** Easily check if a date falls within a day, week, month, quarter, fiscal period, or custom working day window.
* **Working day and holiday logic:** Built-in support for excluding weekends and holidays from all calendar calculations. Simply provide a set of holiday dates and Frist will automatically skip them in working day windows and related queries.
* **Customizable business calendars:** Define your own holiday sets and fiscal year start months for precise business logic.
* **Age calculations:** Compute age spans and durations using flexible input types.
* **No manual math required:** Most operations are declarative and require no arithmetic or direct datetime handling.

---

## Installation

```bash
pip install frist
```

Or clone the repository and install locally:

```bash
git clone https://github.com/hucker/frist.git
cd frist
pip install .
```

---

## Usage

### Calendar Operations

```python
from frist import Cal
import datetime as dt

cal = Cal(target_dt=dt.datetime(2024, 5, 8), ref_dt=dt.datetime(2024, 5, 6), holidays={"2024-05-08"})
print(cal.in_workdays(-2, 2))  # True/False
print(cal.in_months(0))        # True/False
print(cal.in_fiscal_quarters(0)) # True/False
```

### Age Calculations

```python
from frist import Age
import datetime as dt

age = Age(dt.datetime(2000, 1, 1), dt.datetime(2024, 1, 1))
print(age.years)  # Property: number of years
print(age.days)   # Property: number of days

age_now = Age(dt.datetime(2000, 1, 1))
print(age_now.years)
```

---

## API Highlights

### Cal

* `target_dt`, `ref_dt`: Properties for target and reference datetimes
* `in_days`, `in_weeks`, `in_months`, `in_quarters`, `in_years`, `in_workdays`, `in_fiscal_quarters`, `in_fiscal_years`: Methods to check if the target date falls within various calendar windows
* `holiday`, `fiscal_year`, `fiscal_quarter`: Properties for holiday and fiscal calculations


### Age

* `years`, `months`, `days`, `seconds`: Properties for age span
* `working_days`: Property for fractional working days between two datetimes, fully respects custom calendar policies
* Flexible initialization: accepts datetimes, timestamps, or protocols

#### Years Calculation: Approximation Note

The `years` property uses an approximate value of 365.25 days per year, averaging leap and non-leap years for simplicity. If you require exact calendar year calculations (counting 365-day and 366-day years precisely), you will need to implement custom logic to count regular and leap years and handle fractional years carefully. This is left as an exercise for the reader, as it complicates the implementation and is rarely needed for most business use cases.

**Example:**

```python
age = Age(dt.datetime(2000, 1, 1), dt.datetime(2024, 1, 1))
print(age.years)  # Uses 365.25 days/year for approximation
```

#### Arbitrary Calendar Policy Support

The `Age.working_days` property supports arbitrary calendar policies:

* Workdays can be any combination of weekdays (e.g., Mon, Wed, Fri, Sun)
* Holidays can be irregular and non-contiguous
* Business hours can vary per day
* No assumptions about contiguous workweeks or regular schedules

**Correctness is prioritized over efficiency.**
The algorithm iterates day-by-day, checking each date against the calendar policy for workdays, holidays, and business hours. This ensures accurate results for any custom business calendar, even if workdays, holidays, or hours are highly irregular. Optimization is possible, but correctness is preferred unless efficiency is shown to be a bottleneck.

---

## Configuration

* **Holidays:** Pass a set of date strings (YYYY-MM-DD) to exclude from working day calculations
* **Fiscal year start:** Set `fy_start_month` for fiscal calculations

---

## Testing

* Comprehensive test suite covers edge cases, holidays, weekends, and exception handling
* Run tests with:

```bash
pytest
```

---

## Contributing

Pull requests and issues are welcome! See the repository for guidelines.

---

## License

MIT License

---

## Acknowledgments

Inspired by real-world business calendar needs and designed for clarity and ease of use.

Chrono objects support fiscal year and quarter calculations with customizable fiscal year start months. For example:

```python
# Fiscal year starts in April (fy_start_month=4)
meeting = Chrono(target_time=dt.datetime(2025, 7, 15), fy_start_month=4)
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
if project.holiday:
  print("Project start date is a holiday!")
```

## Short Examples

### Age Calculation

```python
person = Chrono(target_time=dt.datetime(1990, 5, 1), reference_time=dt.datetime(2025, 5, 1))
print(f"Age in days: {person.age.days}, Age in years: {person.age.years:.2f}")
```

### Calendar Windows

```python
meeting = Chrono(target_time=dt.datetime(2025, 12, 25))
if meeting.cal.in_days(0):
  print("Meeting is today!")
if meeting.cal.in_weeks(-1):
  print("Meeting was last week.")
```

## API Reference

### Frist

`Chrono(target_time: datetime, reference_time: datetime = None, fy_start_month: int = 1, holidays: set[str] = None)`

- **Properties:**
  * `age`: Age object with properties for `.days`, `.hours`, `.minutes`, `.seconds`, `.weeks`, `.months`, `.quarters`, `.years`, `.fiscal_year`, `.fiscal_quarter`.
  *- `cal`: Cal object for calendar window logic.
  * `fiscal_year`: Fiscal year for the target time.
  * `fiscal_quarter`: Fiscal quarter for the target time.
  * `holiday`: True if target time is a holiday (if holidays set provided).

### Cal

* **Properties:**
  * `dt_val`: Target datetime.
  * `base_time`: Reference datetime.
  * `fiscal_year`: Fiscal year for `dt_val`.
  * `fiscal_quarter`: Fiscal quarter for `dt_val`.
  * `holiday`: True if `dt_val` is a holiday.

* **Interval Methods:**
  * `in_minutes(start: int = 0, end: int | None = None) -> bool`
  * `in_hours(start: int = 0, end: int | None = None) -> bool`
  * `in_days(start: int = 0, end: int | None = None) -> bool`
  * `in_weeks(start: int = 0, end: int | None = None, week_start: str = "monday") -> bool`
  * `in_months(start: int = 0, end: int | None = None) -> bool`
  * `in_quarters(start: int = 0, end: int | None = None) -> bool`
  * `in_years(start: int = 0, end: int | None = None) -> bool`
  * `in_fiscal_quarters(start: int = 0, end: int | None = None) -> bool`
  * `in_fiscal_years(start: int = 0, end: int | None = None) -> bool`

* **Static Methods:**
  * `get_fiscal_year(dt: datetime, fy_start_month: int) -> int`
  * `get_fiscal_quarter(dt: datetime, fy_start_month: int) -> int`

*  **Exceptions:**
  * All interval methods raise `ValueError` if `start > end`.
  * `normalize_weekday(day_spec: str) -> int` raises `ValueError` for invalid day specifications, with detailed error messages.

### Age

`Age(target_time: datetime, reference_time: datetime)`

* **Properties:**
  * `days`, `hours`, `minutes`, `seconds`, `weeks`, `months`, `quarters`, `years`, `fiscal_year`, `fiscal_quarter`

* **Properties:**
  * `target_dt`: Target datetime.
  * `ref_dt`: Reference datetime.

---

## Testing and Support

[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/hucker/zeit/actions)
[![Ruff](https://img.shields.io/badge/ruff-100%25%20clean-brightgreen?logo=ruff&logoColor=white)](https://github.com/charliermarsh/ruff)
