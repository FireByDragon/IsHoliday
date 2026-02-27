"""
Comprehensive test suite for the IsHoliday library.

Covers:
  - DOM (fixed-date) holidays with and without observed-date shifting
  - NOW (nth-weekday) holidays including the week=10 "last Monday" sentinel
  - Year-boundary edge cases (New Year's shifting across Dec/Jan)
  - year_added filtering (holidays not enacted yet)
  - Calendar selection (banking vs. market)
  - is_business_day (weekday + holiday + weekend checks)
  - get_holidays bulk listing

All expected dates were independently verified against published calendars.
"""

import pytest
from datetime import date

from isholiday import is_holiday, get_holiday, get_holidays, is_business_day


# ============================================================================
# DOM holidays — fixed calendar dates
# ============================================================================

class TestFixedDateHolidays:
    """DOM holidays that fall on a specific day of the month."""

    def test_christmas_on_weekday_no_shift(self):
        """Christmas 2025 falls on Thursday — no observed shift."""
        assert is_holiday(date(2025, 12, 25)) is True
        assert get_holiday(date(2025, 12, 25)) == "Christmas Day"

    def test_christmas_saturday_shifts_to_friday(self):
        """Christmas 2021 falls on Saturday — observed Friday Dec 24."""
        assert is_holiday(date(2021, 12, 24)) is True
        assert get_holiday(date(2021, 12, 24)) == "Christmas Day"
        assert is_holiday(date(2021, 12, 25)) is False

    def test_christmas_sunday_shifts_to_monday(self):
        """Christmas 2022 falls on Sunday — observed Monday Dec 26."""
        assert is_holiday(date(2022, 12, 26)) is True
        assert get_holiday(date(2022, 12, 26)) == "Christmas Day"
        assert is_holiday(date(2022, 12, 25)) is False

    def test_independence_day_on_weekday(self):
        """July 4th 2025 falls on Friday — no shift."""
        assert is_holiday(date(2025, 7, 4)) is True
        assert get_holiday(date(2025, 7, 4)) == "Independence Day"

    def test_independence_day_saturday_shifts_to_friday(self):
        """July 4th 2020 falls on Saturday — observed Friday Jul 3."""
        assert is_holiday(date(2020, 7, 3)) is True
        assert get_holiday(date(2020, 7, 3)) == "Independence Day"

    def test_independence_day_sunday_shifts_to_monday(self):
        """July 4th 2021 falls on Sunday — observed Monday Jul 5."""
        assert is_holiday(date(2021, 7, 5)) is True
        assert get_holiday(date(2021, 7, 5)) == "Independence Day"

    def test_new_years_day_on_weekday(self):
        """New Year's 2025 falls on Wednesday — no shift."""
        assert is_holiday(date(2025, 1, 1)) is True
        assert get_holiday(date(2025, 1, 1)) == "New Year's Day"

    def test_new_years_sunday_shifts_to_monday(self):
        """New Year's 2023 falls on Sunday — observed Monday Jan 2."""
        assert is_holiday(date(2023, 1, 2)) is True
        assert get_holiday(date(2023, 1, 2)) == "New Year's Day"

    def test_juneteenth_on_weekday(self):
        """Juneteenth 2025 falls on Thursday — no shift."""
        assert is_holiday(date(2025, 6, 19)) is True


# ============================================================================
# Year-boundary edge cases
# ============================================================================

class TestBoundaryDates:
    """Holidays whose observed date crosses a year boundary."""

    def test_new_years_saturday_observed_dec_31(self):
        """New Year's 2028 falls on Saturday — observed Friday Dec 31, 2027."""
        assert is_holiday(date(2027, 12, 31)) is True
        assert get_holiday(date(2027, 12, 31)) == "New Year's Day"

    def test_new_years_2028_actual_not_holiday(self):
        """Jan 1, 2028 (Saturday) is NOT the observed holiday."""
        assert is_holiday(date(2028, 1, 1)) is False

    def test_boundary_in_get_holidays(self):
        """get_holidays(2027) should include New Year's 2028 observed on Dec 31."""
        holidays_2027 = get_holidays(2027)
        holiday_dates = {d: name for d, name in holidays_2027}
        assert date(2027, 12, 31) in holiday_dates
        assert holiday_dates[date(2027, 12, 31)] == "New Year's Day"


# ============================================================================
# NOW holidays — nth weekday of month
# ============================================================================

class TestNthWeekdayHolidays:
    """NOW holidays calculated as the nth weekday of a month."""

    def test_mlk_day_2025(self):
        """MLK Day 2025 = 3rd Monday in January = Jan 20."""
        assert is_holiday(date(2025, 1, 20)) is True
        assert get_holiday(date(2025, 1, 20)) == "Martin Luther King Jr. Day"

    def test_presidents_day_2025(self):
        """Presidents' Day 2025 = 3rd Monday in February = Feb 17."""
        assert is_holiday(date(2025, 2, 17)) is True
        assert get_holiday(date(2025, 2, 17)) == "Presidents' Day"

    def test_labor_day_2025(self):
        """Labor Day 2025 = 1st Monday in September = Sep 1."""
        assert is_holiday(date(2025, 9, 1)) is True
        assert get_holiday(date(2025, 9, 1)) == "Labor Day"

    def test_thanksgiving_2025(self):
        """Thanksgiving 2025 = 4th Thursday in November = Nov 27."""
        assert is_holiday(date(2025, 11, 27)) is True
        assert get_holiday(date(2025, 11, 27)) == "Thanksgiving Day"

    def test_thanksgiving_2024(self):
        """Thanksgiving 2024 = 4th Thursday in November = Nov 28."""
        assert is_holiday(date(2024, 11, 28)) is True
        assert get_holiday(date(2024, 11, 28)) == "Thanksgiving Day"


# ============================================================================
# Memorial Day — week=10 "last Monday" sentinel
# ============================================================================

class TestMemorialDay:
    """Memorial Day uses week=10 sentinel meaning 'last Monday of May'."""

    def test_memorial_day_2025(self):
        """Memorial Day 2025 = last Monday in May = May 26."""
        assert is_holiday(date(2025, 5, 26)) is True
        assert get_holiday(date(2025, 5, 26)) == "Memorial Day"

    def test_memorial_day_2024(self):
        """Memorial Day 2024 = last Monday in May = May 27."""
        assert is_holiday(date(2024, 5, 27)) is True
        assert get_holiday(date(2024, 5, 27)) == "Memorial Day"

    def test_memorial_day_2023(self):
        """Memorial Day 2023 = last Monday in May = May 29."""
        assert is_holiday(date(2023, 5, 29)) is True

    def test_memorial_day_2026(self):
        """Memorial Day 2026 = last Monday in May = May 25."""
        assert is_holiday(date(2026, 5, 25)) is True


# ============================================================================
# year_added filtering
# ============================================================================

class TestYearAddedFilter:
    """Holidays should not appear before their year_added."""

    def test_juneteenth_before_enactment(self):
        """Juneteenth was added to the market calendar in 2022 — 2021 should be False."""
        assert is_holiday(date(2021, 6, 18), calendar="market") is False
        assert is_holiday(date(2021, 6, 19), calendar="market") is False

    def test_juneteenth_first_market_year(self):
        """Juneteenth 2022 (Sun Jun 19) — observed Mon Jun 20 on market calendar."""
        assert is_holiday(date(2022, 6, 20), calendar="market") is True

    def test_juneteenth_in_banking_2021(self):
        """Juneteenth was added to banking calendar in 2021 — Jun 18 (Fri observed)."""
        assert is_holiday(date(2021, 6, 18), calendar="banking") is True

    def test_juneteenth_not_in_banking_2020(self):
        """Juneteenth not yet enacted in banking calendar for 2020."""
        assert is_holiday(date(2020, 6, 19), calendar="banking") is False


# ============================================================================
# Calendar selection — banking vs. market
# ============================================================================

class TestCalendarSelection:
    """Banking calendar includes Columbus Day and Veterans Day; market does not."""

    def test_columbus_day_in_banking(self):
        """Columbus Day 2025 = 2nd Monday in Oct = Oct 13 — banking only."""
        assert is_holiday(date(2025, 10, 13), calendar="banking") is True
        assert get_holiday(date(2025, 10, 13), calendar="banking") == "Columbus Day"

    def test_columbus_day_not_in_market(self):
        """Columbus Day is NOT a market holiday."""
        assert is_holiday(date(2025, 10, 13), calendar="market") is False

    def test_veterans_day_in_banking(self):
        """Veterans Day 2025 = Nov 11 (Tuesday) — banking only."""
        assert is_holiday(date(2025, 11, 11), calendar="banking") is True
        assert get_holiday(date(2025, 11, 11), calendar="banking") == "Veterans Day"

    def test_veterans_day_not_in_market(self):
        """Veterans Day is NOT a market holiday."""
        assert is_holiday(date(2025, 11, 11), calendar="market") is False

    def test_shared_holiday_in_both_calendars(self):
        """Christmas is in both banking and market calendars."""
        assert is_holiday(date(2025, 12, 25), calendar="banking") is True
        assert is_holiday(date(2025, 12, 25), calendar="market") is True


# ============================================================================
# is_business_day
# ============================================================================

class TestIsBusinessDay:
    """Business day = weekday AND not a holiday."""

    def test_normal_weekday_is_business_day(self):
        """A regular Wednesday with no holiday is a business day."""
        assert is_business_day(date(2025, 2, 19)) is True

    def test_saturday_is_not_business_day(self):
        """Saturday is never a business day."""
        assert is_business_day(date(2025, 2, 22)) is False

    def test_sunday_is_not_business_day(self):
        """Sunday is never a business day."""
        assert is_business_day(date(2025, 2, 23)) is False

    def test_weekday_holiday_is_not_business_day(self):
        """Christmas 2025 (Thursday) is not a business day."""
        assert is_business_day(date(2025, 12, 25)) is False

    def test_day_after_holiday_is_business_day(self):
        """Dec 26, 2025 (Friday, not a holiday) is a business day."""
        assert is_business_day(date(2025, 12, 26)) is True


# ============================================================================
# get_holidays — bulk listing
# ============================================================================

class TestGetHolidays:
    """Verify the full holiday list for a given year."""

    def test_market_holidays_2025_count(self):
        """The market calendar should have 9 holidays in 2025."""
        holidays = get_holidays(2025, calendar="market")
        assert len(holidays) == 9

    def test_banking_holidays_2025_count(self):
        """The banking calendar should have 11 holidays in 2025."""
        holidays = get_holidays(2025, calendar="banking")
        assert len(holidays) == 11

    def test_market_holidays_2025_dates(self):
        """Verify every 2025 market holiday date and name."""
        holidays = get_holidays(2025, calendar="market")
        expected = [
            (date(2025, 1, 1),   "New Year's Day"),
            (date(2025, 1, 20),  "Martin Luther King Jr. Day"),
            (date(2025, 2, 17),  "Presidents' Day"),
            (date(2025, 5, 26),  "Memorial Day"),
            (date(2025, 6, 19),  "Juneteenth National Independence Day"),
            (date(2025, 7, 4),   "Independence Day"),
            (date(2025, 9, 1),   "Labor Day"),
            (date(2025, 11, 27), "Thanksgiving Day"),
            (date(2025, 12, 25), "Christmas Day"),
        ]
        assert holidays == expected

    def test_holidays_sorted_by_date(self):
        """Returned holidays should always be in chronological order."""
        holidays = get_holidays(2025, calendar="market")
        dates = [d for d, _ in holidays]
        assert dates == sorted(dates)

    def test_banking_extra_holidays(self):
        """Banking calendar should include Columbus Day and Veterans Day."""
        holidays = get_holidays(2025, calendar="banking")
        names = {name for _, name in holidays}
        assert "Columbus Day" in names
        assert "Veterans Day" in names


# ============================================================================
# Non-holiday dates
# ============================================================================

class TestNonHolidayDates:
    """Ensure regular dates are correctly identified as non-holidays."""

    def test_random_tuesday(self):
        """An ordinary Tuesday is not a holiday."""
        assert is_holiday(date(2025, 3, 11)) is False

    def test_day_before_christmas(self):
        """Dec 24, 2025 (Wednesday) is not a holiday."""
        assert is_holiday(date(2025, 12, 24)) is False

    def test_day_after_thanksgiving(self):
        """Black Friday (Nov 28, 2025) is not a market holiday."""
        assert is_holiday(date(2025, 11, 28)) is False

    def test_get_holiday_returns_none(self):
        """get_holiday returns None for non-holidays."""
        assert get_holiday(date(2025, 3, 11)) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
