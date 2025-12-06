# `Frist`: Unified Age and Calendar Logic

[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python&logoColor=white)](https://www.python.org/) [![Coverage](https://img.shields.io/badge/coverage-100%25-green)](https://github.com/hucker/frist/actions) [![Pytest](https://img.shields.io/badge/pytest-100%25%20pass%20%7C%20596%20tests-green?logo=pytest&logoColor=white)](https://docs.pytest.org/en/stable/) [![Ruff](https://img.shields.io/badge/ruff-100%25-green?logo=ruff&logoColor=white)](https://github.com/charliermarsh/ruff) [![Tox](https://img.shields.io/static/v1?label=tox&message=3.10-3.14&color=green&logo=tox&logoColor=white)](https://tox.readthedocs.io/) [![Mypy](https://img.shields.io/static/v1?label=mypy&message=0%20issues&color=green&logo=mypy&logoColor=white)](https://mypy-lang.org/)

`Frist` is a modern Python library designed to make working with time, dates, intervals and business calendars easy using a simple, expressive property-based API. `Frist` provides property-based APIs for `Age`, `Cal` (calendar) and `Biz` (business) objects. The `Age` object answers “How old is this?” for two datetimes (often defaulting the second datetime to “now”), making it useful for file aging, log analysis, or event tracking. The `Cal` object lets you ask “Is this date in a specific window?”—such as today, yesterday, this month, this quarter, or this fiscal year—using "intuitive" (if you can call half-open intervals intuitive) properties for calendar logic. Calendar ranges are aligned to calendar units (minute, hour, day, week, month, quarter, year). Finally, the `Biz` class lets you establish a business policy for workdays, business hours, holidays and fiscal years so you can perform business-calendar-aware windowing for working days and business days. 

`Frist` is not a [replacement](https://imgs.xkcd.com/comics/standards_2x.png) for `datetime` or `timedelta` or `dateutil`. Those tools are very good at manipulating dates and times. If the standard library or popular tools meets your needs, keep using them.

`Frist` calculates the time difference between two `TimeLike` values and exposes the age in the units you care about — with no manual conversion factors. For window checks, you describe the intent once and let `Frist` do the alignment: a single property or method call on any unit (second/minute/hour/day/week/month/quarter/year, plus business/work day and fiscal quarter/year). Edge cases (half‑open boundaries, unit alignment, and business policy rules) are handled for you, so you avoid ad‑hoc math and conditional logic.

In practice, this means:

- You ask for values directly: `Age(...).days`, `Age(...).years_precise`, `Cal(...).day.is_today`, `Cal(...).month.in_(-1, 0)`.
- You avoid conversions like dividing by 60/3600/86400, normalizing timestamps, or rounding at unit edges — the unit adapters align and truncate appropriately.
- For business calendars, you express relations via explicit windows tied to a `BizPolicy` (e.g., `biz_day.in_(-1, 0)` for “previous business day”), rather than relying on ambiguous shortcuts.

## Math-Free Ages and Windows

Frist is designed so almost never perform any unit conversion, scale factors, time deltas, spans.



### Signed Business and Working Days

- `Biz.business_days` and `Biz.working_days` are signed fractional counts.
- Positive when `target <= ref`; negative when `target > ref` (reversed order).
- Symmetry holds: reversing `target/ref` yields equal magnitude with opposite sign.
- Holidays contribute `0.0` to `business_days`; `working_days` counts weekday fractions regardless of holidays.
- Shortcuts: `is_today` is available; `is_yesterday`/`is_tomorrow` are intentionally unsupported for business/working days. Prefer explicit windows like `in_(-1, 0)` and `in_(1, 2)`.
(.venv) frist [example/cli]> frist 2024-12-31T01:02:03

=== frist CLI demo ===
target_time:       2024-12-31 01:02:03
reference_time:    2025-12-03 20:22:08.233500

=== Age Properties ===
seconds:           29186405.23
minutes:           486440.09
hours:             8107.33
days:              337.81
months:            11.10
years:             0.92
months_precise:    11.12
years_precise:     0.93

=== Calendar Aligned Window Checks (Cal) ===
Minute in_(-5,0):    0       # Is target 5 min ago to ref_time?
Hour in_(-1,0):      0       # Is target 1 hr ago to ref_time?
Day in_(-1,1):       0       # Is target day before to day after ref_time?
Week in_(-2,0):      0       # Is target 2 weeks ago to ref_time?
Month in_(-6,0):     0       # Is target 6 months ago to ref_time?
Quarter in_(-1,1):   0       # Is target 1 qtr ago to qtr after ref_time?
Year in_(-3,0):      1       # Is target 3 yrs ago to ref_time?

=== Calendar Shortcuts (Cal) ===
is_today:          False
is_yesterday:      False
is_tomorrow:       False
is_this_week:      False
is_this_month:     False
is_this_quarter:   False
is_this_year:      False
is_last_month:     False
is_last_year:      True

=== Calendar Info ===
Minute:            2
Hour:              1
Day:               2 (Tuesday)
Week:              1 (Day: 2)
Month:             12 (Day: 31)
Quarter:           4 (Q4)
Year:              2024 (Day: 366)

=== Biz Info ===
Is Business Day:   True
Is Working Day:    True
Work days:         242.00
Business days:     241.00
Fiscal Quarter:    3 (Q3)
Fiscal Year:       2024
```

Here is an example of using the properties in a typical function.  This example doesn't really show much gain over using `datetime` though those methods will have you doing a lot of dividing by 60, 3600, 86400 to perform date conversions.

```python
import pathlib
import shutil
from frist import Age

def move_old_files_to_backup(src: pathlib.Path, backup: pathlib.Path, days: int = 3) -> None:
    """
    Move all files older than `days` from src to backup using frist for age calculation.

    Args:
        src: Pathlib Path to the folder to scan.
        backup: Pathlib Path to the backup folder.
        days: Number of days; files older than this will be moved.
    """
    for file in src.iterdir():
        if file.is_file():
            age = Age(file.stat().st_mtime)  # Only one argument; end_time defaults to now
            if age.days > days:
                shutil.move(str(file), str(backup / file.name))
```

Here is a similar case of copy all files that were created last month to the backup folder.  This isn't an age question it is a window question.  Using `frist` the implementation of dates at the operating system (as timestamps, or seconds) is hidden, you just give it a time like value and you use the `month` property of the `Cal` object to make a window.  Again it is one line of code to create the object and one method call to check the window.

```python
import pathlib
import shutil
from frist import Cal

def copy_last_month_files_to_backup(src: pathlib.Path, backup: pathlib.Path) -> None:
    """
    Copy all files from last month (relative to now) to the backup folder using frist Cal window logic.
    """
    for file in src.iterdir():
        if file.is_file():
            cal = Cal(target_dt=file.stat().st_mtime)  #end time omitted defaults to 'now'
            if cal.month.in_(-1, 0):  # last month to the current month window
                shutil.move(str(file), str(backup / file.name))
```

Below is the `datetime` version where you need to manually manipulate fields in datetime objects and perform tricky boundary checks.  Not terribly difficult, but something you will need to write every time you write such code.  Presumably you might put this in a function that you would find yourself writing over and over again with lots of tricky edge cases.

```python
import pathlib
import shutil
import datetime as dt

def copy_last_month_files_to_backup(src: pathlib.Path, backup: pathlib.Path) -> None:
    """
    Copy all files from last month (relative to now) to the backup folder using standard library only.
    Uses half-open interval for consistency: [first_of_last_month, first_of_this_month)
    """
    now = dt.datetime.now()
    first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month = first_of_this_month - dt.timedelta(days=1)
    first_of_last_month = last_month.replace(day=1)

    for file in src.iterdir():
        if file.is_file():
            mtime = dt.datetime.fromtimestamp(file.stat().st_mtime)
            if first_of_last_month <= mtime < first_of_this_month
```

## Caveats

- **Fixed-length business days:** Calculations assume standard day lengths; DST transitions
  are ignored. Fractional-day values always use these standard lengths.

- **No timezone support:** All datetimes are treated as naive; timezones are not considered.

- **Fiscal-year and fiscal-quarter logic:** You can set the fiscal year to start on any
  month. Each fiscal year has four quarters, each 3 months long, with Q1 starting on the
  first day of the chosen month.

- **Precomputed Holidays** The business holiday set is a precomputed list of holidays provided by the business.  It is assumed this list will take care of ALL "movable" holiday calculations and provide a list of days (that should land on working days) that are considered days off.  There is NO calculation involved.  If New Years on a Sunday and you are closed Monday then you need to add the 2nd as a holiday.  These calendars are usually provided by HR or accounting.

- **Limits to Flexibility** `Frist` attempts to have a fairly wide input surface for `datetime` representations, including datetime, date, int/float (timestamps) and strings.   Strings, generally can be reconfigured to parse a custom format, but by default expect YYYY-MM-DD HH:MM:SS YYYY-MM-DDTHH:MM:SS (ISO 8601) or YYYY-MM-DD values.

## Age

The `Age` object answers "How old is X?" for two datetimes (start and end). It exposes common elapsed-time metrics as properties so you can write intent‑revealing one‑liners.

- Purpose: elapsed / duration properties (seconds, minutes, hours, days, weeks, months, years).
- Special: `months_precise` and `years_precise` compute calendar-accurate values; `parse()` converts human-friendly duration strings to seconds.
- Default behavior: if `end_time` is omitted it defaults to set to `datetime.now()`.

Examples


```python
# Age and Cal basics without manual math
from frist import Age, Cal
import datetime as dt

age = Age(dt.datetime(2025, 1, 1), dt.datetime(2025, 1, 4, 15))
assert age.days == 3.625

cal = Cal(target_dt=dt.datetime(2025, 1, 2, 12), ref_dt=dt.datetime(2025, 1, 4, 12))
assert cal.day.in_(-2, 0) is True  # Jan 2 within [Jan 2, Jan 4)
```

```python
import datetime as dt
from frist import Age

a = Age(start_time=dt.datetime(2025, 9, 1), end_time=dt.datetime(2025, 11, 20))
assert a.days == 80.0

# number of days in "average" years thus 80/365.25 days
assert round(a.years, 12) == 0.219028062971

# number of days in 2025 thus 80/365
assert round(a.years_precise, 12) == 0.219178082192

# String inputs also work
b = Age("2025-09-01", "2025-11-20")
assert b.days == 80.0
```

### Design Principles: Math-Free Windows

Frist emphasizes clarity and correctness by removing the need for ad‑hoc arithmetic in common calendar and business‑date checks.

- Explicit windows: Half‑open `in_(start, end)` on units (second/minute/day/...) yields predictable, non‑overlapping ranges.
- Direct values: Unit adapters expose `val` and `name` so you ask for what you mean (e.g., `cal.second.val`, `cal.day.name`) without conversions.
- Policy clarity: Business and working day relations are expressed via explicit windows relative to a reference, guided by `BizPolicy`, instead of ambiguous shortcuts.

Examples

```python
from frist import Cal
import datetime as dt

ref = dt.datetime(2025, 12, 5, 12, 0, 10, 0)

# Second-aligned window: start inclusive, end exclusive
Cal(dt.datetime(2025, 12, 5, 12, 0, 9, 500000), ref).second.in_(-2, 1)  # True
Cal(dt.datetime(2025, 12, 5, 12, 0, 11, 0), ref).second.in_(-2, 1)      # False

# Values without conversions
Cal(dt.datetime(2025, 12, 5, 12, 0, 9, 500000), ref).second.val  # 9

# Business-day relations explicitly (avoid date math in shortcuts)
Cal(target_dt, ref_dt).biz_day.in_(-1, 0)  # “previous business day”
```

**Note:** The precise times are somewhat academic, but solve important problems.  If you have the days from February 1 to Feb 28, inclusive what does that mean?  When using precise months that means 1.0 months.  If you have the days from April 1 to April 28 inclusive, you have 28/31 months.  If you use "normal" months which divide by the average days/month you can NEVER get 1.0 months.  Also worth noting, when time periods span months the math is performed on each fractional month so  Feb 22 thru May 1 (inclusive) is 7/28 + 31/31 + 1/30 months

> **Note:**
> If the start is less than the end
> `Age(start, end).months_precise == -Age(end, start).months_precise`

---

## Cal

The `Cal` object provides calendar-aligned window queries (minute/hour/day/week/month/quarter/year and fiscal variants) using half-open semantics. Use `in_*` methods to ask whether a target falls in a calendar window relative to a reference date.

- Purpose: calendar-window membership (in_days, in_months, in_quarters, in_fiscal_years, ...).
- Behavior: calendar-aligned, half-open intervals; supports custom week starts and fiscal start month via Chrono/BizPolicy composition.
- Use-case: one-liners for "was this date in the last two months?" or "is this in the current fiscal quarter?"

Practical note on half-open intervals:

It is normal English to define time spans as half-open intervals. For example, when you say "from 1:00 PM to 2:00 PM" you mean a meeting that starts at 1:00 PM and ends at 2:00 PM (one hour long). You do not mean "any time whose hour is 1 or 2" or that the instant at 2:00 PM is included in the 1:00–2:00 meeting. In half-open semantics the start is inclusive and the end is exclusive — i.e. the interval contains times t where 1:00 PM <= t < 2:00 PM. This convention avoids overlapping windows (e.g., an event that ends exactly at 2:00 PM belongs to the next interval, not the previous one) and makes unit-based queries like `in_hours(1)` intuitive.

Example:

```python
>>> from frist import Cal
>>> import datetime as dt
>>> target = dt.datetime(2025,9,15)
>>> ref = dt.datetime(2025,11,20)
>>> c = Cal(target_dt=target, ref_dt=ref)
>>> c.month.in_(-2, 0)
True    # target was in Sept/Oct (the two full months before Nov)
>>> c.day.in_(-7, -1)
False   # not in the 7..1 days before ref
```

### Window Checks: `in_`

Frist's canonical way to express window membership is the `in_` method on unit adapters. Use `in_(start, end)` with half-open semantics where `start` is inclusive and `end` is exclusive. This keeps ranges non-overlapping and predictable.

Examples:

```python
from frist import Cal
import datetime as dt

ref = dt.datetime(2025, 11, 20)

# Yesterday..tomorrow style checks via half-open windows
Cal(dt.datetime(2025, 11, 19), ref).day.in_(-1, 2)

# Last two full months (end exclusive)
Cal(dt.datetime(2025, 9, 15), ref).month.in_(-2, 0)

# Strictly after start week, end exclusive
Cal(dt.datetime(2025, 11, 24), ref).week.in_(1, 2)

# One-hour window (single unit)
Cal(dt.datetime(2025, 11, 20, 13), ref).hour.in_(-1, 0)
```

---

## Biz

The `Biz` object performs policy-aware business calendar calculations. It relies on `BizPolicy` to determine workdays, holidays, business hours, and fiscal rules.

- Purpose: business/working-day arithmetic (fractional day spans, range membership, fiscal helpers).
- Key differences: `working_days` counts weekdays per policy (ignores holidays); `business_days` excludes holidays. Fractional days computed using policy business hours.
- Common methods: `working_days`, `business_days`, `in_working_days`, `in_business_days`, `get_fiscal_year`, `get_fiscal_quarter`.

Example:

```pycon
>>> from frist import Biz, BizPolicy
>>> import datetime as dt
>>> policy = BizPolicy(workdays={0,1,2,3,4}, holidays={"2025-12-25"})
>>> start = dt.datetime(2025,12,24,9,0)
>>> end   = dt.datetime(2025,12,26,17,0)
>>> b = Biz(start, end, policy)
>>> b.working_days
3.0      # counts Wed/Thu/Fri as workdays (holidays ignored)
>>> b.business_days
2.0      # Dec 25 removed from business-day total
>>> b.biz_day.in_(0)
False    # holiday -> not a business day
>>> b.work_day.in_(0)
True     # weekday per policy

Biz/biz_day/work_day shortcuts:
- `work_day.is_today` and `biz_day.is_today` are provided.
- `is_yesterday`/`is_tomorrow` on `work_day`/`biz_day` raise `ValueError` (use `in_(-1, 0)` / `in_(1, 2)`).

### Design Notes

- Half-open window semantics: All unit adapters use half-open intervals for `in_(start, end)`, meaning `start <= value < end`. This prevents overlapping ranges at boundaries and keeps window checks predictable.
- Explicit windows over vague shortcuts: For business/working days, "yesterday" and "tomorrow" are ambiguous because weekends and holidays break contiguity. Therefore, `work_day.is_yesterday`/`is_tomorrow` and `biz_day.is_yesterday`/`is_tomorrow` raise `ValueError`. Use explicit windows like `in_(-1, 0)` and `in_(1, 2)` to represent prior/next working/business days.
- Day metadata reuse: `biz_day` and `work_day` inherit `val` (ISO weekday 1..7) and `name` (weekday string) from `DayUnit`, overriding only membership logic with policy-aware stepping.

The `BizPolicy` object lets you customize business logic for calendar calculations using half-open intervals You can define:

- **Workdays:** Any combination of weekdays (e.g., Mon, Wed, Fri, Sun)
- **Holidays:** Any set of dates to exclude from working day calculations
- **Business hours:** Custom start/end times for each day
- **Fiscal year start:** Set the starting month for fiscal calculations

**Default Policy:**

If you do not provide a `BizPolicy`, Frist uses a default policy:

- Workdays: Monday–Friday (0–4)
>>> c.day.in_(-1)
- Holidays: none

This is suitable for most standard business use cases. You only need to provide a custom `BizPolicy` if your calendar logic requires non-standard workweeks, holidays, or business hours.

Example (custom policy):

```python
>>> from frist import BizPolicy
>>> policy = BizPolicy(
...     workdays=[0, 1, 2, 3, 4],
...     holidays={"2025-01-10"},
...     start_of_business=dt.time(9, 0),
...     end_of_business=dt.time(17, 0),
...     fiscal_year_start_month=4,
... )
>>> date = dt.datetime(2025, 5, 15)
>>> policy.get_fiscal_year(date)
2025
>>> policy.get_fiscal_quarter(date)
1
>>> policy.is_holiday(dt.datetime(year=2025, month=1, day=1))
False
```

---

## API Reference

Here is a brief overview of the various classes that make up `Frist`.

### TimeLike Input Types

All Frist classes accept flexible time inputs through the `TimeLike` type, which supports:

- `datetime` objects (timezone-naive only)
- `date` objects (converted to `datetime` with 00:00:00 time)
- `float`/`int` values (interpreted as POSIX timestamps)
- `str` values in supported formats:
  - `YYYY-MM-DDTHH:MM:SS` (e.g., `"2023-12-25T14:30:00"` ISO 8601 Datetime)
  - `YYYY-MM-DD` (e.g., `"2023-12-25"` ISO 8601)
  - `YYYY-MM-DD HH:MM:SS` (e.g., `"2023-12-25 14:30:00"`)
  - `1733424000` will be interpreted as a POSIX timestamp
  - `1733424000.1` will be interpreted as a floating point POSIX timestamp

**Custom Formats:** All constructors accept an optional `formats` parameter (list of str) to override the default datetime parsing formats for custom date string formats.

### Age Object

`Age(start_time: TimeLike, end_time: TimeLike | None = None, formats: list[str] | None = None)`

| Property         | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `seconds`        | Age in seconds                                            |
| `minutes`        | Age in minutes                                            |
| `hours`          | Age in hours                                              |
| `days`           | Age in days                                               |
| `weeks`          | Age in weeks                                              |
| `months`         | Age in months (approximate, 30.44 days)                   |
| `months_precise` | Age in months (precise, calendar-based)                   |
| `years`          | Age in years (approximate, 365.25 days)                   |
| `years_precise`  | Age in years (precise, calendar-based)                    |
| `working_days`   | Fractional working days between start and end, per policy |
| `fiscal_year`    | Fiscal year for start_time                                |
| `fiscal_quarter` | Fiscal quarter for start_time                             |
| `start_time`     | Start datetime                                            |
| `end_time`       | End datetime                                              |
| `biz_policy`     | BizPolicy used for business logic                    |

| Method                                      | Description                 |
| ------------------------------------------- | --------------------------- |
| `set_times(start_time=None, end_time=None)` | Update start/end times (accepts TimeLike inputs) |
| `parse(age_str)`                            | Parse age string to seconds |

The `months_precise` and `years_precise` properties calculate the `exact` number of calendar months or years between two dates, accounting for the actual length of each month and year. Unlike the approximate versions (which use averages like 30.44 days/month or 365.25 days/year), these properties provide results that match real-world calendar boundaries. They are more intuitively correct but are slower to compute since the first and last month/year need to be handled differently.  Basically, Feb 1 to Feb 28 (non leap year) is 1.0 precise months long, while Jan 1 to Jan31 is also 1 precise month long. And Jan 1 to Feb 14 is 1.5 precise months.  For years it is similar but the effect is smaller.  The 365 days in 2021 is 1 precise year as are the 366 days in 2024.

---

### Cal Object

The Cal object provides a family of `in_*` methods (e.g., `in_days`, `in_months`, `in_years` etc) to check if the target date falls within a calendar window relative to the reference date. These methods use calendar units (not elapsed time) using half-open intervals. The start is inclusive, the end is exclusive. This makes it easy to check if a date is in a specific calendar range (e.g., last week, next month, fiscal quarter) using intuitive, unit-based logic.

 `day.in_(-1)`: Is the target date yesterday?
 `day.in_(-1, 1)`: Is the target date within ±1 calendar day of the reference?

`Cal(target_dt: TimeLike, ref_dt: TimeLike, formats: list[str] | None = None)`

| Property         | Description                   | Return |
| ---------------- | ----------------------------- | ------ |
| `target_dt`      | Target datetime               | `datetime` |
| `ref_dt`         | Reference datetime            | `datetime` |
| `fiscal_year`    | Fiscal year for `target_dt`   | `int` |
| `fiscal_quarter` | Fiscal quarter for `target_dt`| `int` |
| `holiday`        | True if `target_dt` is a holiday | `bool` |

| Unit accessor                                      | Description                 | Return |
| -------------------------------------------------- | --------------------------- | ------ |
| `cal.second.in_(start=0, end=None)`                | Is target in second window  | `bool` |
| `cal.minute.in_(start=0, end=None)`                | Is target in minute window  | `bool` |
| `cal.hour.in_(start=0, end=None)`                  | Is target in hour window    | `bool` |
| `cal.day.in_(start=0, end=None)`                   | Is target in day window     | `bool` |
| `cal.week.in_(start=0, end=None, week_start="monday")` | Is target in week window    | `bool` |
| `cal.month.in_(start=0, end=None)`                 | Is target in month window   | `bool` |
| `cal.month.nth_weekday(weekday, n)`                | Nth weekday of month (date) | `datetime` |
| `cal.month.is_nth_weekday(weekday, n)`             | Is target nth weekday of month | `bool` |
| `cal.qtr.in_(start=0, end=None)`                   | Is target in quarter window | `bool` |
| `cal.year.in_(start=0, end=None)`                  | Is target in year window    | `bool` |
| `cal.year.day_of_year()`                           | Day of year for target      | `int` |
| `cal.year.is_day_of_year(n)`                       | Is target nth day of year   | `bool` |

---

### MonthUnit: nth_weekday and is_nth_weekday

#### Get the Nth Weekday of a Month

```python
from frist import Cal

cal = Cal(target_dt, ref_dt)

# Get the 2nd Friday of the reference month
second_friday = cal.month.nth_weekday("friday", 2)

# Get the last Monday of the reference month
last_monday = cal.month.nth_weekday("monday", -1)
```

- `n` can be positive (1 = first, 2 = second, ...) or negative (-1 = last, -2 = second-to-last, ...).
- Raises `ValueError` if the nth weekday does not exist in the month.

#### Check if Target Date is the Nth Weekday

```python
# Returns True if target_dt is the last Monday of its month
is_last_monday = cal.month.is_nth_weekday("monday", -1)
```

---

### Year Namespace: day_of_year and is_day_of_year

#### Get the Day of Year

```python
# Returns the day of the year for target_dt (1-based, Jan 1 = 1)
day_num = cal.year.day_of_year()
```

#### Check if Target Date is the Nth Day of the Year

```python
# Returns True if target_dt is the 100th day of its year
is_100th = cal.year.is_day_of_year(100)
```

---

### Edge Cases

- For `nth_weekday`, if the requested occurrence does not exist (e.g., 5th Friday in a 4-Friday month), a `ValueError` is raised.
- For `is_nth_weekday`, returns `False` if the nth occurrence does not exist.

---

### API Reference Additions

- `MonthUnit.nth_weekday(weekday: str, n: int) -> datetime`
- `MonthUnit.is_nth_weekday(weekday: str, n: int) -> bool`
- `YearUnit.day_of_year() -> int`
- `YearUnit.is_day_of_year(n: int) -> bool`

---

Shortcuts (convenience boolean properties):

| Shortcut | Equivalent |
| -------- | ---------------------- |
| `is_today`       | `cal.day.in_(0)`   |
| `is_yesterday`   | `cal.day.in_(-1)`  |
| `is_tomorrow`    | `cal.day.in_(1)`   |

---

### Biz Object

The `Biz` object performs business-aware calculations using a `BizPolicy`. It counts
working days (defined by the policy's workday set) and business days (working days that are not holidays).
It also computes fractional day contributions using the policy's business hours.

***Business days and workdays are tricky to calculate and involve iteration because no/few assumptions can be made about the way the days fall. Normally this isn't a huge deal because the time spans are a few days, not 1000's of days.***

`Biz(target_time: TimeLike, ref_time: TimeLike | None, policy: BizPolicy | None, formats: list[str] | None = None)`

| Property / Attribute | Description                                                         | Return |
| -------------------- | ------------------------------------------------------------------- | ------ |
| `biz_policy`         | `BizPolicy` instance used by this Biz                          | `BizPolicy` |
| `target_dt`        | Target datetime                                                     | `datetime` |
| `ref_dt`           | Reference datetime                                                  | `datetime` |
| `holiday`            | True if `target_time` is a holiday                                  | `bool` |
| `is_workday`         | True if `target_time` falls on a workday                            | `bool` |
| `is_business_day`    | True if `target_time` is a business day (workday and not holiday)   | `bool` |
| `working_days`       | Fractional working days between target and ref (ignores holidays)   | `float` |
| `business_days`      | Fractional business days between target and ref (excludes holidays) | `float` |

| Methods/Accessors                         | Description                                           | Return |
| ---------------------------------------- | ----------------------------------------------------- | ------ |
| `work_day.in_(start=0, end=None)`        | Range membership by working days (ignores holidays)   | `bool` |
| `biz_day.in_(start=0, end=None)`         | Range membership by business days (excludes holidays) | `bool` |
| `fis_year.in_(start=0, end=None)`        | Fiscal year window membership                         | `bool` |
| `fis_qtr.in_(start=0, end=None)`         | Fiscal quarter window membership                      | `bool` |
| `biz.work_day`                           | Unit adapter for working-day logic                    | `Unit` |
| `biz.biz_day`                            | Unit adapter for business-day logic                   | `Unit` |
| `biz.fis_year`                           | Unit adapter for fiscal-year logic                    | `Unit` |
| `biz.fis_qtr`                            | Unit adapter for fiscal-quarter logic                 | `Unit` |

Shortcuts:

- `work_day.is_today` and `biz_day.is_today` are provided.
- `work_day.is_yesterday`/`is_tomorrow` and `biz_day.is_yesterday`/`is_tomorrow` are not supported and raise `ValueError`. Use explicit windows with `in_(start, end)` (e.g., `in_(-1, 0)`, `in_(1, 2)`).
- Fiscal shortcuts remain available via unit adapters (e.g., `biz.fis_qtr.in_(...)`, `biz.fis_year.in_(...)`).

### Chrono Object

In some situations you will need to have all three of these classes together because the filtering you are doing is related to the multiple classes.  The best way to handle this is with the chrono object.  The `Chrono` class initializes all three so you have access to each of the classes, with no race conditions when setting the reference time.

```python
# Brief Chrono example: create a Chrono and print Age / Cal / Biz properties
>>> from frist import Chrono, BizPolicy
>>> import datetime as dt
>>> target = dt.datetime(2025, 4, 25, 15, 0)
>>> ref = dt.datetime(2025, 4, 30, 12, 0)
>>> policy = BizPolicy(workdays={0,1,2,3,4}, holidays={"2025-04-28"})
>>> z = Chrono(target_dt=target, ref_dt=ref, policy=policy)

# Age (elapsed-time properties)
>>> z.age.days                # elapsed days (float)
3.875
>>> z.age.years_precise       # calendar-accurate years
0.0106

# Cal (calendar-window queries)
>>> z.cal.day.in_(-5)         # was target 5 days before reference?
True
>>> z.cal.month.in_(0)        # same calendar month as reference?
True

# Biz (policy-aware business logic — properties are floats)
>>> z.biz.working_days        # fractional working days (counts workdays per policy)
1.0
>>> z.biz.business_days       # fractional business days (excludes holidays from policy)
0.0
>>> z.biz.work_day.in_(0)  # range-membership helper (bool)
True
>>> z.biz.biz_day.in_(0) # range-membership helper (bool)
False
```

`Chrono(target_td: TimeLike, ref_dt: TimeLike = None, biz_policy:BizPolicy|None, formats: list[str] | None = None)`

| Property | Description                                           |
| -------- | ----------------------------------------------------- |
| `age`    | `Age` object for span calculations (see `Age` above)      |
| `cal`    | `Cal` object for calendar window logic (see `Cal` above)  |
| `biz`    | `Biz`  object for calendar window logic (see `Cal` above) |

### Pytest (100% pass/100% coverage)

```text
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src\frist\__init__.py                    9      0   100%
src\frist\_age.py                      122      0   100%
src\frist\_biz.py                       96      0   100%
src\frist\_biz_policy.py                80      0   100%
src\frist\_cal.py                       83      0   100%
src\frist\_constants.py                 15      0   100%
src\frist\_frist.py                     47      0   100%
src\frist\_types.py                     35      0   100%
src\frist\_util.py                      17      0   100%
src\frist\units\__init__.py             14      0   100%
src\frist\units\_base.py                38      0   100%
src\frist\units\_biz_day.py             60      0   100%
src\frist\units\_day.py                 27      0   100%
src\frist\units\_fiscal_quarter.py      33      0   100%
src\frist\units\_fiscal_year.py         21      0   100%
src\frist\units\_hour.py                18      0   100%
src\frist\units\_minute.py              18      0   100%
src\frist\units\_month.py               43      0   100%
src\frist\units\_quarter.py             27      0   100%
src\frist\units\_second.py              18      0   100%
src\frist\units\_week.py                23      0   100%
src\frist\units\_work_day.py            70      0   100%
src\frist\units\_year.py                23      0   100%
```

> Note: running `pytest -m smoke` on the current branch produced ~62% coverage and completed in ~0.46s
> (test run: `512 passed`).

### Tox

```text
main> tox
  py310: OK (5.11=setup[3.24]+cmd[1.87] seconds)
  py311: OK (6.46=setup[3.89]+cmd[2.57] seconds)
  py312: OK (7.01=setup[4.65]+cmd[2.36] seconds)
  py313: OK (6.67=setup[4.37]+cmd[2.30] seconds)
  py314: OK (6.04=setup[4.27]+cmd[1.77] seconds)
  congratulations :) (32.91 seconds)
```

### Mypy

```text
main> mypy src/frist
Success: no issues found in 10 source files
```

### Notes

This project was developed as learning project using agentic AI. Most of the code was generated from prompts rather that writing code.  It was tricky getting tests implemented correctly. Generally I write a test case and then ask the AI to parameterize it and then I review.  I discovered that I had some code that had a bug in one case and the AI changed the test inputs (added 1) to make the test pass. I find with agentic AI that I spend more time on my testing than on coding, even to the point that I will happily delete a test file and start over if I don't like it.  With manually written code I would be far less inclined to do that.

I think of tests as specifications for the code (sort of like super prompts) that the agents use to generate better code estimates of what you a building. I find it hard to fathom not iterating with with prompts and tests.

I also noted that certain types of refactoring humans are much better at.  I changed the naming convention of some methods and asked the AI to fix it.  Several models couldn't handle it without infinite looping, random (idiotic) indentation and even dumber patch placements, sometimes at the top of the file, others in the middle of methods.  Eventually I just manually refactored the big parts and then it did much better.

## Development and Testing Notes

While the `frist` library maintains high test coverage (100%) and utilizes property-based testing with Hypothesis, this level of coverage was not a strict requirement for the library's development. Rather, it emerged as part of a learning experience exploring agentic AI capabilities in software testing and quality assurance. The comprehensive test suite demonstrates some possibilities of automated testing tools but is not indicative of typical development practices for this type of utility library.

Contributions are welcome. Please prefer small, reviewable pull requests and include tests that exercise expected behavior and edge cases.
