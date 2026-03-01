"""
Five-year boundary tests for the Canada calendar (2024-2028).

For every holiday in each year, verifies:
  - The day OF the holiday is recognized (with correct name).
  - The day BEFORE the holiday is NOT a holiday.
  - The day AFTER the holiday is NOT a holiday.

When holidays are adjacent (e.g., Christmas + Boxing Day, Golden Week), the
before/after boundary walks past the cluster to find the nearest non-holiday.

All expected dates were independently verified against published calendars.
"""

import pytest
from datetime import date

from isholiday import is_holiday, get_holiday


# ---------------------------------------------------------------------------
# Holiday dates -- day of (should be a holiday with matching name)
# ---------------------------------------------------------------------------

HOLIDAYS_CANADA = [
    (date(2024, 1, 1), "New Year's Day"),
    (date(2024, 2, 19), "Family Day"),
    (date(2024, 3, 29), "Good Friday"),
    (date(2024, 4, 1), "Easter Monday"),
    (date(2024, 5, 20), "Victoria Day"),
    (date(2024, 7, 1), "Canada Day"),
    (date(2024, 9, 2), "Labour Day"),
    (date(2024, 9, 30), "National Day for Truth and Reconciliation"),
    (date(2024, 10, 14), "Thanksgiving Day"),
    (date(2024, 11, 11), "Remembrance Day"),
    (date(2024, 12, 25), "Christmas Day"),
    (date(2024, 12, 26), "Boxing Day"),
    (date(2025, 1, 1), "New Year's Day"),
    (date(2025, 2, 17), "Family Day"),
    (date(2025, 4, 18), "Good Friday"),
    (date(2025, 4, 21), "Easter Monday"),
    (date(2025, 5, 19), "Victoria Day"),
    (date(2025, 7, 1), "Canada Day"),
    (date(2025, 9, 1), "Labour Day"),
    (date(2025, 9, 30), "National Day for Truth and Reconciliation"),
    (date(2025, 10, 13), "Thanksgiving Day"),
    (date(2025, 11, 11), "Remembrance Day"),
    (date(2025, 12, 25), "Christmas Day"),
    (date(2025, 12, 26), "Boxing Day"),
    (date(2026, 1, 1), "New Year's Day"),
    (date(2026, 2, 16), "Family Day"),
    (date(2026, 4, 3), "Good Friday"),
    (date(2026, 4, 6), "Easter Monday"),
    (date(2026, 5, 18), "Victoria Day"),
    (date(2026, 7, 1), "Canada Day"),
    (date(2026, 9, 7), "Labour Day"),
    (date(2026, 9, 30), "National Day for Truth and Reconciliation"),
    (date(2026, 10, 12), "Thanksgiving Day"),
    (date(2026, 11, 11), "Remembrance Day"),
    (date(2026, 12, 25), "Christmas Day"),
    (date(2026, 12, 26), "Boxing Day"),
    (date(2027, 1, 1), "New Year's Day"),
    (date(2027, 2, 15), "Family Day"),
    (date(2027, 3, 26), "Good Friday"),
    (date(2027, 3, 29), "Easter Monday"),
    (date(2027, 5, 24), "Victoria Day"),
    (date(2027, 7, 1), "Canada Day"),
    (date(2027, 9, 6), "Labour Day"),
    (date(2027, 9, 30), "National Day for Truth and Reconciliation"),
    (date(2027, 10, 11), "Thanksgiving Day"),
    (date(2027, 11, 11), "Remembrance Day"),
    (date(2027, 12, 25), "Christmas Day"),
    (date(2027, 12, 27), "Boxing Day"),
    (date(2028, 1, 1), "New Year's Day"),
    (date(2028, 2, 21), "Family Day"),
    (date(2028, 4, 14), "Good Friday"),
    (date(2028, 4, 17), "Easter Monday"),
    (date(2028, 5, 22), "Victoria Day"),
    (date(2028, 7, 1), "Canada Day"),
    (date(2028, 9, 4), "Labour Day"),
    (date(2028, 9, 30), "National Day for Truth and Reconciliation"),
    (date(2028, 10, 9), "Thanksgiving Day"),
    (date(2028, 11, 11), "Remembrance Day"),
    (date(2028, 12, 25), "Christmas Day"),
    (date(2028, 12, 26), "Boxing Day"),
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day before each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_BEFORE_CANADA = [
    date(2023, 12, 31),  # before New Year's Day 2024
    date(2024, 2, 18),  # before Family Day 2024
    date(2024, 3, 28),  # before Good Friday 2024
    date(2024, 3, 31),  # before Easter Monday 2024
    date(2024, 5, 19),  # before Victoria Day 2024
    date(2024, 6, 30),  # before Canada Day 2024
    date(2024, 9, 1),  # before Labour Day 2024
    date(2024, 9, 29),  # before National Day for Truth and Reconciliation 2024
    date(2024, 10, 13),  # before Thanksgiving Day 2024
    date(2024, 11, 10),  # before Remembrance Day 2024
    date(2024, 12, 24),  # before Christmas Day 2024
    date(2024, 12, 31),  # before New Year's Day 2025
    date(2025, 2, 16),  # before Family Day 2025
    date(2025, 4, 17),  # before Good Friday 2025
    date(2025, 4, 20),  # before Easter Monday 2025
    date(2025, 5, 18),  # before Victoria Day 2025
    date(2025, 6, 30),  # before Canada Day 2025
    date(2025, 8, 31),  # before Labour Day 2025
    date(2025, 9, 29),  # before National Day for Truth and Reconciliation 2025
    date(2025, 10, 12),  # before Thanksgiving Day 2025
    date(2025, 11, 10),  # before Remembrance Day 2025
    date(2025, 12, 24),  # before Christmas Day 2025
    date(2025, 12, 31),  # before New Year's Day 2026
    date(2026, 2, 15),  # before Family Day 2026
    date(2026, 4, 2),  # before Good Friday 2026
    date(2026, 4, 5),  # before Easter Monday 2026
    date(2026, 5, 17),  # before Victoria Day 2026
    date(2026, 6, 30),  # before Canada Day 2026
    date(2026, 9, 6),  # before Labour Day 2026
    date(2026, 9, 29),  # before National Day for Truth and Reconciliation 2026
    date(2026, 10, 11),  # before Thanksgiving Day 2026
    date(2026, 11, 10),  # before Remembrance Day 2026
    date(2026, 12, 24),  # before Christmas Day 2026
    date(2026, 12, 31),  # before New Year's Day 2027
    date(2027, 2, 14),  # before Family Day 2027
    date(2027, 3, 25),  # before Good Friday 2027
    date(2027, 3, 28),  # before Easter Monday 2027
    date(2027, 5, 23),  # before Victoria Day 2027
    date(2027, 6, 30),  # before Canada Day 2027
    date(2027, 9, 5),  # before Labour Day 2027
    date(2027, 9, 29),  # before National Day for Truth and Reconciliation 2027
    date(2027, 10, 10),  # before Thanksgiving Day 2027
    date(2027, 11, 10),  # before Remembrance Day 2027
    date(2027, 12, 24),  # before Christmas Day 2027
    date(2027, 12, 26),  # before Boxing Day 2027
    date(2027, 12, 31),  # before New Year's Day 2028
    date(2028, 2, 20),  # before Family Day 2028
    date(2028, 4, 13),  # before Good Friday 2028
    date(2028, 4, 16),  # before Easter Monday 2028
    date(2028, 5, 21),  # before Victoria Day 2028
    date(2028, 6, 30),  # before Canada Day 2028
    date(2028, 9, 3),  # before Labour Day 2028
    date(2028, 9, 29),  # before National Day for Truth and Reconciliation 2028
    date(2028, 10, 8),  # before Thanksgiving Day 2028
    date(2028, 11, 10),  # before Remembrance Day 2028
    date(2028, 12, 24),  # before Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day after each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_AFTER_CANADA = [
    date(2024, 1, 2),  # after New Year's Day 2024
    date(2024, 2, 20),  # after Family Day 2024
    date(2024, 3, 30),  # after Good Friday 2024
    date(2024, 4, 2),  # after Easter Monday 2024
    date(2024, 5, 21),  # after Victoria Day 2024
    date(2024, 7, 2),  # after Canada Day 2024
    date(2024, 9, 3),  # after Labour Day 2024
    date(2024, 10, 1),  # after National Day for Truth and Reconciliation 2024
    date(2024, 10, 15),  # after Thanksgiving Day 2024
    date(2024, 11, 12),  # after Remembrance Day 2024
    date(2024, 12, 27),  # after Christmas Day 2024
    date(2025, 1, 2),  # after New Year's Day 2025
    date(2025, 2, 18),  # after Family Day 2025
    date(2025, 4, 19),  # after Good Friday 2025
    date(2025, 4, 22),  # after Easter Monday 2025
    date(2025, 5, 20),  # after Victoria Day 2025
    date(2025, 7, 2),  # after Canada Day 2025
    date(2025, 9, 2),  # after Labour Day 2025
    date(2025, 10, 1),  # after National Day for Truth and Reconciliation 2025
    date(2025, 10, 14),  # after Thanksgiving Day 2025
    date(2025, 11, 12),  # after Remembrance Day 2025
    date(2025, 12, 27),  # after Christmas Day 2025
    date(2026, 1, 2),  # after New Year's Day 2026
    date(2026, 2, 17),  # after Family Day 2026
    date(2026, 4, 4),  # after Good Friday 2026
    date(2026, 4, 7),  # after Easter Monday 2026
    date(2026, 5, 19),  # after Victoria Day 2026
    date(2026, 7, 2),  # after Canada Day 2026
    date(2026, 9, 8),  # after Labour Day 2026
    date(2026, 10, 1),  # after National Day for Truth and Reconciliation 2026
    date(2026, 10, 13),  # after Thanksgiving Day 2026
    date(2026, 11, 12),  # after Remembrance Day 2026
    date(2026, 12, 27),  # after Christmas Day 2026
    date(2027, 1, 2),  # after New Year's Day 2027
    date(2027, 2, 16),  # after Family Day 2027
    date(2027, 3, 27),  # after Good Friday 2027
    date(2027, 3, 30),  # after Easter Monday 2027
    date(2027, 5, 25),  # after Victoria Day 2027
    date(2027, 7, 2),  # after Canada Day 2027
    date(2027, 9, 7),  # after Labour Day 2027
    date(2027, 10, 1),  # after National Day for Truth and Reconciliation 2027
    date(2027, 10, 12),  # after Thanksgiving Day 2027
    date(2027, 11, 12),  # after Remembrance Day 2027
    date(2027, 12, 26),  # after Christmas Day 2027
    date(2027, 12, 28),  # after Boxing Day 2027
    date(2028, 1, 2),  # after New Year's Day 2028
    date(2028, 2, 22),  # after Family Day 2028
    date(2028, 4, 15),  # after Good Friday 2028
    date(2028, 4, 18),  # after Easter Monday 2028
    date(2028, 5, 23),  # after Victoria Day 2028
    date(2028, 7, 2),  # after Canada Day 2028
    date(2028, 9, 5),  # after Labour Day 2028
    date(2028, 10, 1),  # after National Day for Truth and Reconciliation 2028
    date(2028, 10, 10),  # after Thanksgiving Day 2028
    date(2028, 11, 12),  # after Remembrance Day 2028
    date(2028, 12, 27),  # after Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCanadaDayOf:
    """Each holiday date should be recognized with the correct name."""

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_CANADA)
    def test_is_holiday(self, target_date, expected_name):
        assert is_holiday(target_date, calendar="canada") is True

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_CANADA)
    def test_get_holiday_name(self, target_date, expected_name):
        assert get_holiday(target_date, calendar="canada") == expected_name


class TestCanadaDayBefore:
    """The nearest non-holiday before each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_BEFORE_CANADA)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="canada") is False


class TestCanadaDayAfter:
    """The nearest non-holiday after each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_AFTER_CANADA)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="canada") is False
