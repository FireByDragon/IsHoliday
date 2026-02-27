"""
IsHoliday — Determine if a date is a US holiday.

Supports multiple holiday calendars via TOML configuration files:
  - ``"market"``  — NYSE / NASDAQ holidays (9 holidays, default)
  - ``"banking"`` — US Federal Reserve banking holidays (11 holidays)
  - ``"/path/to/custom.toml"`` — user-defined calendar

Usage::

    from datetime import date
    from isholiday import is_holiday, get_holiday, get_holidays, is_business_day

    is_holiday(date(2025, 12, 25))                          # True
    get_holiday(date(2025, 12, 25))                         # "Christmas Day"
    get_holidays(2025)                                       # [(date, name), ...]
    is_business_day(date(2025, 12, 25))                     # False

    # Banking calendar (includes Columbus Day, Veterans Day)
    is_holiday(date(2025, 10, 13), calendar="banking")      # True

    # Custom TOML calendar
    is_holiday(date(2025, 1, 1), calendar="/path/to/my.toml")
"""

from datetime import date
from typing import Optional

from .calendar import holidays_for_year, lookup_holiday

__version__ = "1.0.0"
__all__ = ["is_holiday", "get_holiday", "get_holidays", "is_business_day"]


def is_holiday(target_date: date, calendar: str = "market") -> bool:
    """Return True if *target_date* is a holiday on the given calendar."""
    return lookup_holiday(target_date, calendar) is not None


def get_holiday(target_date: date, calendar: str = "market") -> Optional[str]:
    """Return the holiday name if *target_date* is a holiday, else None."""
    return lookup_holiday(target_date, calendar)


def get_holidays(year: int, calendar: str = "market") -> list[tuple[date, str]]:
    """Return all (date, name) pairs for holidays in *year*, sorted by date."""
    return holidays_for_year(year, calendar)


def is_business_day(target_date: date, calendar: str = "market") -> bool:
    """Return True if *target_date* is a weekday and not a holiday."""
    if target_date.isoweekday() >= 6:
        return False
    return lookup_holiday(target_date, calendar) is None
