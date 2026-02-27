# IsHoliday

**Define the rule once. Calculate holidays forever.**

Most holiday libraries use year-by-year lookup tables that require annual maintenance and data updates. IsHoliday takes a fundamentally different approach: holidays are defined as **rules**, not rows. "Christmas is December 25th" and "Thanksgiving is the 4th Thursday in November" are rules that never change. Define them once and IsHoliday computes the correct observed dates for any year — past, present, or future — with zero maintenance.

No annual data files. No version bumps just to add next year. No tables to manage.

## Why IsHoliday?

| | Traditional Libraries | IsHoliday |
|---|---|---|
| **Data model** | Year-by-year lookup tables | Rule-based definitions |
| **Annual maintenance** | Required (new year = new data) | None (rules compute any year) |
| **Future dates** | Only if table includes them | Unlimited — works for any year |
| **Custom calendars** | Edit source code or subclass | Drop in a TOML file |
| **Dependencies** | Often pulls in heavy packages | Zero — pure Python stdlib |
| **Configuration** | Hardcoded or complex APIs | Simple, human-readable TOML |

## Installation

```bash
pip install isholiday
```

Requires Python 3.11+. Zero external dependencies.

## Quick Start

```python
from datetime import date
from isholiday import is_holiday, get_holiday, get_holidays, is_business_day

# Is today a holiday?
is_holiday(date(2025, 12, 25))          # True

# What holiday is it?
get_holiday(date(2025, 12, 25))         # "Christmas Day"

# All holidays for a year
get_holidays(2025)
# [(date(2025, 1, 1),   "New Year's Day"),
#  (date(2025, 1, 20),  "Martin Luther King Jr. Day"),
#  (date(2025, 2, 17),  "Presidents' Day"),
#  (date(2025, 5, 26),  "Memorial Day"),
#  (date(2025, 6, 19),  "Juneteenth National Independence Day"),
#  (date(2025, 7, 4),   "Independence Day"),
#  (date(2025, 9, 1),   "Labor Day"),
#  (date(2025, 11, 27), "Thanksgiving Day"),
#  (date(2025, 12, 25), "Christmas Day")]

# Is it a business day? (weekday + not a holiday)
is_business_day(date(2025, 12, 25))     # False (holiday)
is_business_day(date(2025, 12, 27))     # False (Saturday)
is_business_day(date(2025, 12, 26))     # True  (regular Friday)

# Works for any year — no tables to maintain
get_holidays(2050)                       # Just works
```

## Built-in Calendars

IsHoliday ships with two calendars out of the box:

| Calendar | Holidays | Description |
|----------|----------|-------------|
| `"market"` (default) | 9 | NYSE / NASDAQ stock market holidays |
| `"banking"` | 11 | US Federal Reserve banking holidays |

The **market** calendar excludes Columbus Day and Veterans Day — the stock exchanges remain open on those days. The **banking** calendar includes all 11 Federal Reserve holidays.

```python
# Columbus Day: banks closed, markets open
is_holiday(date(2025, 10, 13), calendar="banking")   # True
is_holiday(date(2025, 10, 13), calendar="market")    # False
```

## Custom Calendars

Need company holidays? A different country? Industry-specific closures? Create a TOML file and point IsHoliday at it:

```python
is_holiday(date(2025, 1, 1), calendar="/path/to/my_holidays.toml")
```

### TOML Format

Holidays are defined using two rule types:

| Type | Rule | Example |
|------|------|---------|
| `DOM` | Fixed calendar date | Christmas = December 25 every year |
| `NOW` | Nth weekday of a month | Thanksgiving = 4th Thursday in November |

```toml
[calendar]
name        = "my-company"
description = "Company holiday calendar"

[types]
DOM = "Calendar Day of Month"
NOW = "Nth Weekday of Month"

# Fixed date: observe on Friday if Saturday, Monday if Sunday
[[holidays]]
name               = "New Year's Day"
type               = "DOM"
month              = 1
day                = 1
saturday_to_friday = true
sunday_to_monday   = true
year_added         = 1870
enabled            = true

# Relative date: 4th Thursday in November
[[holidays]]
name               = "Thanksgiving Day"
type               = "NOW"
month              = 11
week               = 4
weekday            = 5          # 1=Sun, 2=Mon, 3=Tue, 4=Wed, 5=Thu, 6=Fri, 7=Sat
saturday_to_friday = false
sunday_to_monday   = false
year_added         = 1941
enabled            = true
```

### Observed-Date Rules

When a fixed-date holiday falls on a weekend, it can shift to the nearest weekday:

- **Saturday** holidays shift to Friday (`saturday_to_friday = true`)
- **Sunday** holidays shift to Monday (`sunday_to_monday = true`)

These are configurable per holiday. Relative holidays (NOW type) always land on a weekday by definition, so shifting doesn't apply.

### Special: Last Weekday of Month

Use `week = 10` as a sentinel for "last occurrence" — for example, Memorial Day is the **last Monday in May**:

```toml
[[holidays]]
name    = "Memorial Day"
type    = "NOW"
month   = 5
week    = 10       # sentinel: last occurrence in the month
weekday = 2        # Monday
```

## API Reference

### `is_holiday(target_date, calendar="market") -> bool`
Returns `True` if the date is a holiday on the given calendar.

### `get_holiday(target_date, calendar="market") -> Optional[str]`
Returns the holiday name, or `None`.

### `get_holidays(year, calendar="market") -> list[tuple[date, str]]`
Returns all `(date, name)` pairs for the year, sorted chronologically.

### `is_business_day(target_date, calendar="market") -> bool`
Returns `True` if the date is a weekday **and** not a holiday.

All functions accept `calendar` as `"market"`, `"banking"`, or a file path to a custom TOML calendar.

## How It Works

IsHoliday encodes each holiday as a **rule** — not a table row for each year. At query time, it:

1. Reads the rule definitions from a TOML file (cached after first load)
2. Computes the actual date for the target year using calendar math
3. Applies observed-date shifting (Saturday to Friday, Sunday to Monday)
4. Handles year-boundary edge cases (e.g., New Year's on Saturday is observed Dec 31)

The computation is pure math — no network calls, no database, no external data. It works offline, in CI pipelines, in embedded systems, anywhere Python runs.

## License

MIT
