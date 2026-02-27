# IsHoliday

Determine if a date is a US holiday. Zero dependencies, pure Python 3.11+.

Supports multiple holiday calendars via TOML configuration files — banking (Federal Reserve), stock market (NYSE/NASDAQ), or your own custom calendar.

## Installation

```bash
pip install isholiday
```

## Quick Start

```python
from datetime import date
from isholiday import is_holiday, get_holiday, get_holidays, is_business_day

# Check if a date is a market holiday
is_holiday(date(2025, 12, 25))          # True (Christmas Day)
is_holiday(date(2025, 12, 24))          # False

# Get the holiday name
get_holiday(date(2025, 12, 25))         # "Christmas Day"
get_holiday(date(2025, 3, 11))          # None

# List all holidays for a year
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

# Check if a date is a business day (weekday + not a holiday)
is_business_day(date(2025, 12, 25))     # False (holiday)
is_business_day(date(2025, 12, 27))     # False (Saturday)
is_business_day(date(2025, 12, 26))     # True  (Friday, not a holiday)
```

## Calendars

### Built-in Calendars

| Calendar | Holidays | Use Case |
|----------|----------|----------|
| `"market"` (default) | 9 | NYSE / NASDAQ trading days |
| `"banking"` | 11 | Federal Reserve banking holidays |

The **market** calendar excludes Columbus Day and Veterans Day (markets trade on those days). The **banking** calendar includes all 11 Federal Reserve holidays.

```python
# Banking calendar includes Columbus Day
is_holiday(date(2025, 10, 13), calendar="banking")   # True
is_holiday(date(2025, 10, 13), calendar="market")    # False
```

### Custom Calendars

Create your own TOML calendar file and pass its path:

```python
is_holiday(date(2025, 1, 1), calendar="/path/to/my_holidays.toml")
```

TOML format:

```toml
[calendar]
name        = "custom"
description = "My custom holiday calendar"

[types]
DOM = "Calendar Day of Month"
NOW = "Nth Weekday of Month"

[[holidays]]
name               = "New Year's Day"
type               = "DOM"
month              = 1
day                = 1
saturday_to_friday = true
sunday_to_monday   = true
year_added         = 1870
enabled            = true

[[holidays]]
name               = "Thanksgiving Day"
type               = "NOW"
month              = 11
week               = 4          # 4th occurrence
weekday            = 5          # Thursday (SQL convention: 1=Sun, 2=Mon, ..., 7=Sat)
saturday_to_friday = false
sunday_to_monday   = false
year_added         = 1941
enabled            = true
```

## Holiday Types

| Type | Description | Example |
|------|-------------|---------|
| `DOM` | Fixed calendar date | Christmas = December 25 |
| `NOW` | Nth weekday of month | Thanksgiving = 4th Thursday in November |

**Observed-date rules**: When a DOM holiday falls on Saturday, it shifts to Friday. When it falls on Sunday, it shifts to Monday. These are configurable per holiday via `saturday_to_friday` and `sunday_to_monday`.

**Special sentinel**: `week = 10` means "last occurrence of that weekday" (e.g., Memorial Day = last Monday in May).

## API Reference

### `is_holiday(target_date, calendar="market") -> bool`
Returns `True` if the date is a holiday on the given calendar.

### `get_holiday(target_date, calendar="market") -> Optional[str]`
Returns the holiday name, or `None` if not a holiday.

### `get_holidays(year, calendar="market") -> list[tuple[date, str]]`
Returns all `(date, name)` pairs for the given year, sorted chronologically.

### `is_business_day(target_date, calendar="market") -> bool`
Returns `True` if the date is a weekday **and** not a holiday.

## Requirements

- Python 3.11+ (uses `tomllib` from stdlib)
- Zero external dependencies

## License

MIT
