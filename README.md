


# Frist: Property-Based Date and Time Operations

Frist is a modern Python library for calendar, age, and time window calculations. Its API is property-driven—most operations are performed by accessing properties or calling simple methods, with minimal need for manual math or low-level datetime manipulation.

**In German, "Frist" means "deadline" or "time limit." This reflects the package's focus on time windows, periods, and calendar logic.**

---


## Key Features

- **Property-based API:** Access date and time information through properties and high-level methods.
- **Calendar windows:** Easily check if a date falls within a day, week, month, quarter, fiscal period, or custom working day window.
- **Working day and holiday logic:** Built-in support for excluding weekends and holidays from all calendar calculations. Simply provide a set of holiday dates and Frist will automatically skip them in working day windows and related queries.
- **Customizable business calendars:** Define your own holiday sets and fiscal year start months for precise business logic.
- **Age calculations:** Compute age spans and durations using flexible input types.
- **No manual math required:** Most operations are declarative and require no arithmetic or direct datetime handling.

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

- `target_dt`, `ref_dt`: Properties for target and reference datetimes
- `in_days`, `in_weeks`, `in_months`, `in_quarters`, `in_years`, `in_workdays`, `in_fiscal_quarters`, `in_fiscal_years`: Methods to check if the target date falls within various calendar windows
- `holiday`, `fiscal_year`, `fiscal_quarter`: Properties for holiday and fiscal calculations

### Age

- `years`, `months`, `days`, `seconds`: Properties for age span
- Flexible initialization: accepts datetimes, timestamps, or protocols

---

## Configuration

- **Holidays:** Pass a set of date strings (YYYY-MM-DD) to exclude from working day calculations
- **Fiscal year start:** Set `fy_start_month` for fiscal calculations

---

## Testing

- Comprehensive test suite covers edge cases, holidays, weekends, and exception handling
- Run tests with:
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
  '2025-07-04',  # Independence Day
}

# Check a specific date
meeting = Chrono(target_time=dt.datetime(2025, 12, 25), holidays=holidays)
if meeting.holiday:
  print("Meeting date is a holiday!")

# Check multiple dates
for date_str in holidays:
  date = dt.datetime.strptime(date_str, '%Y-%m-%d')
  c = Chrono(target_time=date, holidays=holidays)
  print(f"{date.date()}: Holiday? {c.holiday}")

# Use with custom reference time
project = Chrono(target_time=dt.datetime(2025, 7, 4), reference_time=dt.datetime(2025, 7, 5), holidays=holidays)
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
  - `age`: Age object with properties for `.days`, `.hours`, `.minutes`, `.seconds`, `.weeks`, `.months`, `.quarters`, `.years`, `.fiscal_year`, `.fiscal_quarter`.
  - `cal`: Cal object for calendar window logic.
  - `fiscal_year`: Fiscal year for the target time.
  - `fiscal_quarter`: Fiscal quarter for the target time.
  - `holiday`: True if target time is a holiday (if holidays set provided).

### Cal


- **Properties:**
  - `dt_val`: Target datetime.
  - `base_time`: Reference datetime.
  - `fiscal_year`: Fiscal year for `dt_val`.
  - `fiscal_quarter`: Fiscal quarter for `dt_val`.
  - `holiday`: True if `dt_val` is a holiday.

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


- **Properties:**
  - `target_dt`: Target datetime.
  - `ref_dt`: Reference datetime.

---

## Testing and Support

[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](https://github.com/hucker/zeit/actions)
[![Ruff](https://img.shields.io/badge/ruff-100%25%20clean-brightgreen?logo=ruff&logoColor=white)](https://github.com/charliermarsh/ruff)
