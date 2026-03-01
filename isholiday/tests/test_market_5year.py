"""
Five-year boundary tests for the Market calendar (2024-2028).

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

HOLIDAYS_MARKET = [
    (date(2024, 1, 1), "New Year's Day"),
    (date(2024, 1, 15), "Martin Luther King Jr. Day"),
    (date(2024, 2, 19), "Presidents' Day"),
    (date(2024, 5, 27), "Memorial Day"),
    (date(2024, 6, 19), "Juneteenth National Independence Day"),
    (date(2024, 7, 4), "Independence Day"),
    (date(2024, 9, 2), "Labor Day"),
    (date(2024, 11, 28), "Thanksgiving Day"),
    (date(2024, 12, 25), "Christmas Day"),
    (date(2025, 1, 1), "New Year's Day"),
    (date(2025, 1, 20), "Martin Luther King Jr. Day"),
    (date(2025, 2, 17), "Presidents' Day"),
    (date(2025, 5, 26), "Memorial Day"),
    (date(2025, 6, 19), "Juneteenth National Independence Day"),
    (date(2025, 7, 4), "Independence Day"),
    (date(2025, 9, 1), "Labor Day"),
    (date(2025, 11, 27), "Thanksgiving Day"),
    (date(2025, 12, 25), "Christmas Day"),
    (date(2026, 1, 1), "New Year's Day"),
    (date(2026, 1, 19), "Martin Luther King Jr. Day"),
    (date(2026, 2, 16), "Presidents' Day"),
    (date(2026, 5, 25), "Memorial Day"),
    (date(2026, 6, 19), "Juneteenth National Independence Day"),
    (date(2026, 7, 3), "Independence Day"),
    (date(2026, 9, 7), "Labor Day"),
    (date(2026, 11, 26), "Thanksgiving Day"),
    (date(2026, 12, 25), "Christmas Day"),
    (date(2027, 1, 1), "New Year's Day"),
    (date(2027, 1, 18), "Martin Luther King Jr. Day"),
    (date(2027, 2, 15), "Presidents' Day"),
    (date(2027, 5, 31), "Memorial Day"),
    (date(2027, 6, 18), "Juneteenth National Independence Day"),
    (date(2027, 7, 5), "Independence Day"),
    (date(2027, 9, 6), "Labor Day"),
    (date(2027, 11, 25), "Thanksgiving Day"),
    (date(2027, 12, 24), "Christmas Day"),
    (date(2027, 12, 31), "New Year's Day"),
    (date(2028, 1, 17), "Martin Luther King Jr. Day"),
    (date(2028, 2, 21), "Presidents' Day"),
    (date(2028, 5, 29), "Memorial Day"),
    (date(2028, 6, 19), "Juneteenth National Independence Day"),
    (date(2028, 7, 4), "Independence Day"),
    (date(2028, 9, 4), "Labor Day"),
    (date(2028, 11, 23), "Thanksgiving Day"),
    (date(2028, 12, 25), "Christmas Day"),
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day before each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_BEFORE_MARKET = [
    date(2023, 12, 31),  # before New Year's Day 2024
    date(2024, 1, 14),  # before Martin Luther King Jr. Day 2024
    date(2024, 2, 18),  # before Presidents' Day 2024
    date(2024, 5, 26),  # before Memorial Day 2024
    date(2024, 6, 18),  # before Juneteenth National Independence Day 2024
    date(2024, 7, 3),  # before Independence Day 2024
    date(2024, 9, 1),  # before Labor Day 2024
    date(2024, 11, 27),  # before Thanksgiving Day 2024
    date(2024, 12, 24),  # before Christmas Day 2024
    date(2024, 12, 31),  # before New Year's Day 2025
    date(2025, 1, 19),  # before Martin Luther King Jr. Day 2025
    date(2025, 2, 16),  # before Presidents' Day 2025
    date(2025, 5, 25),  # before Memorial Day 2025
    date(2025, 6, 18),  # before Juneteenth National Independence Day 2025
    date(2025, 7, 3),  # before Independence Day 2025
    date(2025, 8, 31),  # before Labor Day 2025
    date(2025, 11, 26),  # before Thanksgiving Day 2025
    date(2025, 12, 24),  # before Christmas Day 2025
    date(2025, 12, 31),  # before New Year's Day 2026
    date(2026, 1, 18),  # before Martin Luther King Jr. Day 2026
    date(2026, 2, 15),  # before Presidents' Day 2026
    date(2026, 5, 24),  # before Memorial Day 2026
    date(2026, 6, 18),  # before Juneteenth National Independence Day 2026
    date(2026, 7, 2),  # before Independence Day 2026
    date(2026, 9, 6),  # before Labor Day 2026
    date(2026, 11, 25),  # before Thanksgiving Day 2026
    date(2026, 12, 24),  # before Christmas Day 2026
    date(2026, 12, 31),  # before New Year's Day 2027
    date(2027, 1, 17),  # before Martin Luther King Jr. Day 2027
    date(2027, 2, 14),  # before Presidents' Day 2027
    date(2027, 5, 30),  # before Memorial Day 2027
    date(2027, 6, 17),  # before Juneteenth National Independence Day 2027
    date(2027, 7, 4),  # before Independence Day 2027
    date(2027, 9, 5),  # before Labor Day 2027
    date(2027, 11, 24),  # before Thanksgiving Day 2027
    date(2027, 12, 23),  # before Christmas Day 2027
    date(2027, 12, 30),  # before New Year's Day 2027
    date(2028, 1, 16),  # before Martin Luther King Jr. Day 2028
    date(2028, 2, 20),  # before Presidents' Day 2028
    date(2028, 5, 28),  # before Memorial Day 2028
    date(2028, 6, 18),  # before Juneteenth National Independence Day 2028
    date(2028, 7, 3),  # before Independence Day 2028
    date(2028, 9, 3),  # before Labor Day 2028
    date(2028, 11, 22),  # before Thanksgiving Day 2028
    date(2028, 12, 24),  # before Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Non-holiday dates -- day after each holiday (walks past adjacent holidays)
# ---------------------------------------------------------------------------

NOT_HOLIDAYS_AFTER_MARKET = [
    date(2024, 1, 2),  # after New Year's Day 2024
    date(2024, 1, 16),  # after Martin Luther King Jr. Day 2024
    date(2024, 2, 20),  # after Presidents' Day 2024
    date(2024, 5, 28),  # after Memorial Day 2024
    date(2024, 6, 20),  # after Juneteenth National Independence Day 2024
    date(2024, 7, 5),  # after Independence Day 2024
    date(2024, 9, 3),  # after Labor Day 2024
    date(2024, 11, 29),  # after Thanksgiving Day 2024
    date(2024, 12, 26),  # after Christmas Day 2024
    date(2025, 1, 2),  # after New Year's Day 2025
    date(2025, 1, 21),  # after Martin Luther King Jr. Day 2025
    date(2025, 2, 18),  # after Presidents' Day 2025
    date(2025, 5, 27),  # after Memorial Day 2025
    date(2025, 6, 20),  # after Juneteenth National Independence Day 2025
    date(2025, 7, 5),  # after Independence Day 2025
    date(2025, 9, 2),  # after Labor Day 2025
    date(2025, 11, 28),  # after Thanksgiving Day 2025
    date(2025, 12, 26),  # after Christmas Day 2025
    date(2026, 1, 2),  # after New Year's Day 2026
    date(2026, 1, 20),  # after Martin Luther King Jr. Day 2026
    date(2026, 2, 17),  # after Presidents' Day 2026
    date(2026, 5, 26),  # after Memorial Day 2026
    date(2026, 6, 20),  # after Juneteenth National Independence Day 2026
    date(2026, 7, 4),  # after Independence Day 2026
    date(2026, 9, 8),  # after Labor Day 2026
    date(2026, 11, 27),  # after Thanksgiving Day 2026
    date(2026, 12, 26),  # after Christmas Day 2026
    date(2027, 1, 2),  # after New Year's Day 2027
    date(2027, 1, 19),  # after Martin Luther King Jr. Day 2027
    date(2027, 2, 16),  # after Presidents' Day 2027
    date(2027, 6, 1),  # after Memorial Day 2027
    date(2027, 6, 19),  # after Juneteenth National Independence Day 2027
    date(2027, 7, 6),  # after Independence Day 2027
    date(2027, 9, 7),  # after Labor Day 2027
    date(2027, 11, 26),  # after Thanksgiving Day 2027
    date(2027, 12, 25),  # after Christmas Day 2027
    date(2028, 1, 1),  # after New Year's Day 2027
    date(2028, 1, 18),  # after Martin Luther King Jr. Day 2028
    date(2028, 2, 22),  # after Presidents' Day 2028
    date(2028, 5, 30),  # after Memorial Day 2028
    date(2028, 6, 20),  # after Juneteenth National Independence Day 2028
    date(2028, 7, 5),  # after Independence Day 2028
    date(2028, 9, 5),  # after Labor Day 2028
    date(2028, 11, 24),  # after Thanksgiving Day 2028
    date(2028, 12, 26),  # after Christmas Day 2028
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMarketDayOf:
    """Each holiday date should be recognized with the correct name."""

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_MARKET)
    def test_is_holiday(self, target_date, expected_name):
        assert is_holiday(target_date, calendar="market") is True

    @pytest.mark.parametrize("target_date, expected_name", HOLIDAYS_MARKET)
    def test_get_holiday_name(self, target_date, expected_name):
        assert get_holiday(target_date, calendar="market") == expected_name


class TestMarketDayBefore:
    """The nearest non-holiday before each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_BEFORE_MARKET)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="market") is False


class TestMarketDayAfter:
    """The nearest non-holiday after each holiday should NOT be a holiday."""

    @pytest.mark.parametrize("target_date", NOT_HOLIDAYS_AFTER_MARKET)
    def test_not_holiday(self, target_date):
        assert is_holiday(target_date, calendar="market") is False
