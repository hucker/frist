# `Frist`: Unified Age and Calendar Logic

`Frist`is a modern Python library designed to make working with time, dates, and intervals simple and expressive—whether you’re analyzing file ages, tracking events, or handling business calendars. `Frist` provides two core property-based APIs: `Age` and `Cal`. The `Age` object lets you answer “How old is this?” for any two datetimes (often defaulting to “now”), making it perfect for file aging, log analysis, or event tracking. The `Cal` object lets you ask “Is this date in a specific window?”—such as today, yesterday, this month, this quarter, or this fiscal year—using intuitive properties for calendar logic. Calendar ranges are always aligned to a calendar time scale, day, business day, month, year, quarter, hour.

You never need to do manual calendar math. `Frist`’s property-based API gives you direct answers to common time and calendar questions. For business and operational use cases, `Frist`’s  policy object lets you define workdays, holidays, and business hours, so your calendar calculations match your real-world rules. Whether you need precise age calculations, flexible date windows, or custom business logic, `Frist` unifies these features in a clean, easy-to-use API built entirely around properties.

```pycon
>>> from frist import Chrono
>>> import datetime as dt
>>> meeting_time = dt.datetime(2025, 4, 25, 15, 0)  # Meeting 5 days ago
>>> today = dt.datetime(2025, 4, 30)
>>> meeting = Chrono(target_time=meeting_time, reference_time=today)
>>> f"Meeting age: {meeting.age.days:.2f} days"
'Meeting age: 5.00 days'
>>> meeting.cal.in_days(0)
False
>>> meeting.cal.in_days(-5)
True
>>> meeting.cal.in_months(0)
True
>>> meeting.cal.in_months(0, 2)
True
>>> meeting.cal.in_months(-2)
False
>>> other_day = dt.datetime(2025, 5, 1)
>>> meeting_other = Chrono(target_time=meeting_time, reference_time=other_day)
>>> meeting_other.cal.in_days(0)
False
>>> meeting_other.cal.in_months(0)
True
>>> meeting_other.cal.in_months(0, 2)
False
>>> meeting_other.cal.in_months(-2)
True
```

## CalendarPolicy

The `CalendarPolicy` object lets you customize business logic for calendar calculations using half open intervals You can define:

- **Workdays:** Any combination of weekdays (e.g., Mon, Wed, Fri, Sun)
- **Holidays:** Any set of dates to exclude from working day calculations
- **Business hours:** Custom start/end times for each day
- **Fiscal year start:** Set the starting month for fiscal calculations

**Default Policy:**

If you do not provide a `CalendarPolicy`, Frist uses a default policy:

- Workdays: Monday–Friday (0–4)
- Work hours: 9AM–5PM
- Holidays: none

This is suitable for most standard business use cases. You only need to provide a custom `CalendarPolicy` if your calendar logic requires non-standard workweeks, holidays, or business hours.

Example (custom policy):

```pycon
>>> from frist import CalendarPolicy
>>> import datetime as dt
>>> policy = CalendarPolicy(workdays={0,1,2,3,4}, holidays={"2025-1-1"}, work_hours=(9,17), fy_start_month=4)
>>> date = dt.datetime(2025, 5, 15)
>>> policy.get_fiscal_year(date)
2026
>>> policy.get_fiscal_quarter(date)
1
>>> policy.is_holiday(dt.datetime(year=2025,month=1,day=1))
True
```

---

## API Reference

### Age Object
```pycon
>>> from frist import Age
>>> import datetime as dt
>>> start = dt.datetime(2000, 1, 1)
>>> end = dt.datetime(2025, 5, 1)
>>> age = Age(start_time=start, end_time=end)
>>> age.years
25.33
>>> age.days
9252
>>> age.months
303.98
>>> age.working_days
6573.0
```

`Age(start_time: datetime, end_time: datetime = None, cal_policy: CalendarPolicy = None)`

| Property         | Description                                              |
|------------------|----------------------------------------------------------|
| `seconds`        | Age in seconds                                           |
| `minutes`        | Age in minutes                                           |
| `hours`          | Age in hours                                             |
| `days`           | Age in days                                              |
| `weeks`          | Age in weeks                                             |
| `months`         | Age in months (approximate, 30.44 days)                  |
| `months_precise` | Age in months (precise, calendar-based)                  |
| `years`          | Age in years (approximate, 365.25 days)                  |
| `years_precise`  | Age in years (precise, calendar-based)                   |
| `working_days`   | Fractional working days between start and end, per policy|
| `fiscal_year`    | Fiscal year for start_time                               |
| `fiscal_quarter` | Fiscal quarter for start_time                            |
| `start_time`     | Start datetime                                           |
| `end_time`       | End datetime                                             |
| `cal_policy`     | CalendarPolicy used for business logic                   |

| Method           | Description                                              |
|------------------|----------------------------------------------------------|
| `set_times(start_time=None, end_time=None)` | Update start/end times         |
| `parse(age_str)` | Parse age string to seconds                              |

The `months_precise` and `years_precise` properties calculate the exact number of calendar months or years between two dates, accounting for the actual length of each month and year. Unlike the approximate versions (which use averages like 30.44 days/month or 365.25 days/year), these properties provide results that match real-world calendar boundaries. They are more intuitively correct but may be slower to compute, especially for long time spans.

---

### Cal Object

The Cal object provides a family of `in_*` methods (e.g., `in_days`, `in_months`, `in_years` etc) to check if the target date falls within a calendar window relative to the reference date. These methods use calendar units (not elapsed time) using half-open intervals. The start is inclusive, the end is exclusive. This makes it easy to check if a date is in a specific calendar range (e.g., last week, next month, fiscal quarter) using intuitive, unit-based logic.

```pycon
>>> from frist import Cal
>>> import datetime as dt
>>> target = dt.datetime(2025, 4, 29)
>>> reference = dt.datetime(2025, 4, 30)
>>> cal = Cal(target_dt=target, ref_dt=reference)
>>> cal.in_days(-1)
True  # Target is yesterday
>>> cal.in_days(0)
False # Target is not today
>>> cal.in_days(-1, 1)
True  # Target is within ±1 day of reference
```

- `in_days(-1)`: Is the target date yesterday?
- `in_days(-1, 1)`: Is the target date within ±1 calendar day of the reference?

`Cal(target_dt: datetime, ref_dt: datetime, fy_start_month: int = 1, holidays: set[str] = None)`

| Property         | Description                                 |
|------------------|---------------------------------------------|
| `dt_val`         | Target datetime                             |
| `base_time`      | Reference datetime                          |
| `fiscal_year`    | Fiscal year for `dt_val`                    |
| `fiscal_quarter` | Fiscal quarter for `dt_val`                 |
| `holiday`        | True if `dt_val` is a holiday               |

| Interval Method  | Description                                 |
|------------------|---------------------------------------------|
| `in_minutes(start=0, end=None)`         | Is target in minute window         |
| `in_hours(start=0, end=None)`           | Is target in hour window           |
| `in_days(start=0, end=None)`            | Is target in day window            |
| `in_weeks(start=0, end=None, week_start="monday")` | Is target in week window |
| `in_months(start=0, end=None)`          | Is target in month window          |
| `in_quarters(start=0, end=None)`        | Is target in quarter window        |
| `in_years(start=0, end=None)`           | Is target in year window           |
| `in_fiscal_quarters(start=0, end=None)` | Is target in fiscal quarter window |
| `in_fiscal_years(start=0, end=None)`    | Is target in fiscal year window    |

---

### Biz Object

The `Biz` object performs business-aware calculations using a `CalendarPolicy`. It counts
working days (defined by the policy's workday set) and business days (working days that are not holidays).
It also computes fractional day contributions using the policy's business hours.

```pycon
>>> from frist import Biz, CalendarPolicy
>>> import datetime as dt
>>> policy = CalendarPolicy(workdays={0,1,2,3,4}, holidays={"2025-01-01"})
>>> target = dt.datetime(2025, 1, 2, 9, 0)
>>> ref = dt.datetime(2025, 1, 4, 17, 0)
>>> b = Biz(target, ref, policy)
>>> b.working_days()
1.875
>>> b.business_days()
0.875  # holiday on Jan 1 removed from business-day total
```

`Biz(target_time: datetime, ref_time: datetime | None, policy: CalendarPolicy | None)`

| Property / Attribute | Description |
|----------------------|-------------|
| `cal_policy`         | `CalendarPolicy` instance used by this Biz |
| `target_time`        | Target datetime |
| `ref_time`           | Reference datetime |
| `holiday`            | True if `target_time` is a holiday |
| `is_workday`         | True if `target_time` falls on a workday |
| `is_business_day`    | True if `target_time` is a business day (workday and not holiday) |

| Method               | Description |
|----------------------|-------------|
| `working_days()`     | Fractional working days between target and ref (ignores holidays) |
| `business_days()`    | Fractional business days between target and ref (excludes holidays) |
| `in_working_days(start=0, end=0)` | Range membership by working days (ignores holidays) |
| `in_business_days(start=0, end=0)`| Range membership by business days (excludes holidays) |
| `get_fiscal_year(dt, fy_start_month)` | Static helper to compute fiscal year for a datetime |
| `get_fiscal_quarter(dt, fy_start_month)` | Static helper to compute fiscal quarter |


### Chrono Object

`Chrono(target_time: datetime, reference_time: datetime = None, fy_start_month: int = 1, holidays: set[str] = None)`

| Property      | Description                                                      |
|--------------|------------------------------------------------------------------|
| `age`        | Age object for span calculations (see Age above)                  |
| `cal`        | Cal object for calendar window logic (see Cal above)              |
| `fiscal_year`| Fiscal year for the target time                                   |
| `fiscal_quarter` | Fiscal quarter for the target time                            |
| `holiday`    | True if target time is a holiday (if holidays set provided)       |

### Status

[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue?logo=python&logoColor=white)](https://www.python.org/) [![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/hucker/frist/actions) [![Pytest](https://img.shields.io/badge/pytest-100%25%20pass%20%7C%20341%20tests-blue?logo=pytest&logoColor=white)](https://docs.pytest.org/en/stable/) [![Ruff](https://img.shields.io/badge/ruff-100%25-brightgreen?logo=ruff&logoColor=white)](https://github.com/charliermarsh/ruff) [![Tox](https://img.shields.io/badge/tox-tested%20%7C%20multi%20envs-green?logo=tox&logoColor=white)](https://tox.readthedocs.io/)

### Pytest

```text
src\frist\__init__.py                         8      0      0      0   100%
src\frist\_age.py                           149      0     46      0   100%
src\frist\_biz.py                           138      0     28      0   100%
src\frist\_cal.py                           114      0     20      0   100%
src\frist\_cal_policy.py                     79      0     38      0   100%
src\frist\_constants.py                      15      0      0      0   100%
src\frist\_frist.py                          71      0     18      0   100%
src\frist\_util.py                           12      0      4      0   100%
```

### Tox

```text
  py310: OK (15.17=setup[12.99]+cmd[2.18] seconds)
  py311: OK (10.57=setup[7.96]+cmd[2.61] seconds)
  py312: OK (11.98=setup[9.45]+cmd[2.53] seconds)
  py313: OK (10.74=setup[8.46]+cmd[2.29] seconds)
  py314: OK (11.04=setup[8.61]+cmd[2.43] seconds)
  congratulations :) (59.61 seconds)
```
