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
        """The market calendar should have 10 holidays in 2025."""
        holidays = get_holidays(2025, calendar="market")
        assert len(holidays) == 10

    def test_banking_holidays_2025_count(self):
        """The banking calendar should have 13 holidays in 2025."""
        holidays = get_holidays(2025, calendar="banking")
        assert len(holidays) == 13

    def test_market_holidays_2025_dates(self):
        """Verify every 2025 market holiday date and name."""
        holidays = get_holidays(2025, calendar="market")
        expected = [
            (date(2025, 1, 1),   "New Year's Day"),
            (date(2025, 1, 20),  "Martin Luther King Jr. Day"),
            (date(2025, 2, 17),  "Presidents' Day"),
            (date(2025, 4, 18),  "Good Friday"),
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


# ============================================================================
# International — United Kingdom bank holidays
# ============================================================================

class TestUKHolidays:
    """UK bank holidays (England & Wales) using the 'uk' built-in calendar."""

    def test_uk_new_years_day_2025(self):
        """New Year's Day 2025 = Wednesday Jan 1."""
        assert is_holiday(date(2025, 1, 1), calendar="uk") is True
        assert get_holiday(date(2025, 1, 1), calendar="uk") == "New Year's Day"

    def test_uk_early_may_bank_holiday_2025(self):
        """Early May Bank Holiday 2025 = 1st Monday in May = May 5."""
        assert is_holiday(date(2025, 5, 5), calendar="uk") is True
        assert get_holiday(date(2025, 5, 5), calendar="uk") == "Early May Bank Holiday"

    def test_uk_spring_bank_holiday_2025(self):
        """Spring Bank Holiday 2025 = last Monday in May = May 26."""
        assert is_holiday(date(2025, 5, 26), calendar="uk") is True
        assert get_holiday(date(2025, 5, 26), calendar="uk") == "Spring Bank Holiday"

    def test_uk_summer_bank_holiday_2025(self):
        """Summer Bank Holiday 2025 = last Monday in August = Aug 25."""
        assert is_holiday(date(2025, 8, 25), calendar="uk") is True
        assert get_holiday(date(2025, 8, 25), calendar="uk") == "Summer Bank Holiday"

    def test_uk_christmas_2025(self):
        """Christmas Day 2025 = Thursday Dec 25."""
        assert is_holiday(date(2025, 12, 25), calendar="uk") is True
        assert get_holiday(date(2025, 12, 25), calendar="uk") == "Christmas Day"

    def test_uk_boxing_day_2025(self):
        """Boxing Day 2025 = Friday Dec 26."""
        assert is_holiday(date(2025, 12, 26), calendar="uk") is True
        assert get_holiday(date(2025, 12, 26), calendar="uk") == "Boxing Day"

    def test_uk_holidays_2025_count(self):
        """UK calendar has 8 holidays."""
        holidays = get_holidays(2025, calendar="uk")
        assert len(holidays) == 8

    def test_uk_not_a_us_holiday(self):
        """US Independence Day is not a UK holiday."""
        assert is_holiday(date(2025, 7, 4), calendar="uk") is False

    def test_uk_new_years_sunday_shifts_to_monday(self):
        """UK New Year's 2023 (Sunday) → observed Monday Jan 2."""
        assert is_holiday(date(2023, 1, 2), calendar="uk") is True
        assert get_holiday(date(2023, 1, 2), calendar="uk") == "New Year's Day"


# ============================================================================
# International — Canada federal statutory holidays
# ============================================================================

class TestCanadaHolidays:
    """Canada federal statutory holidays using the 'canada' built-in calendar."""

    def test_canada_day_2025(self):
        """Canada Day 2025 = Tuesday Jul 1."""
        assert is_holiday(date(2025, 7, 1), calendar="canada") is True
        assert get_holiday(date(2025, 7, 1), calendar="canada") == "Canada Day"

    def test_canada_victoria_day_2025(self):
        """Victoria Day 2025 = Monday on or before May 24 = May 19."""
        assert is_holiday(date(2025, 5, 19), calendar="canada") is True
        assert get_holiday(date(2025, 5, 19), calendar="canada") == "Victoria Day"

    def test_canada_labour_day_2025(self):
        """Labour Day 2025 = 1st Monday in Sep = Sep 1."""
        assert is_holiday(date(2025, 9, 1), calendar="canada") is True
        assert get_holiday(date(2025, 9, 1), calendar="canada") == "Labour Day"

    def test_canada_thanksgiving_2025(self):
        """Canadian Thanksgiving 2025 = 2nd Monday in Oct = Oct 13."""
        assert is_holiday(date(2025, 10, 13), calendar="canada") is True
        assert get_holiday(date(2025, 10, 13), calendar="canada") == "Thanksgiving Day"

    def test_canada_remembrance_day_2025(self):
        """Remembrance Day 2025 = Tuesday Nov 11."""
        assert is_holiday(date(2025, 11, 11), calendar="canada") is True
        assert get_holiday(date(2025, 11, 11), calendar="canada") == "Remembrance Day"

    def test_canada_truth_reconciliation_2025(self):
        """National Day for Truth and Reconciliation 2025 = Tuesday Sep 30."""
        assert is_holiday(date(2025, 9, 30), calendar="canada") is True

    def test_canada_truth_reconciliation_before_enactment(self):
        """Truth and Reconciliation not enacted before 2021."""
        assert is_holiday(date(2020, 9, 30), calendar="canada") is False

    def test_canada_holidays_2025_count(self):
        """Canada calendar has 12 holidays in 2025."""
        holidays = get_holidays(2025, calendar="canada")
        assert len(holidays) == 12

    def test_canada_boxing_day_2025(self):
        """Boxing Day 2025 = Friday Dec 26."""
        assert is_holiday(date(2025, 12, 26), calendar="canada") is True
        assert get_holiday(date(2025, 12, 26), calendar="canada") == "Boxing Day"

    def test_canada_family_day_2025(self):
        """Family Day 2025 = 3rd Monday in Feb = Feb 17."""
        assert is_holiday(date(2025, 2, 17), calendar="canada") is True
        assert get_holiday(date(2025, 2, 17), calendar="canada") == "Family Day"


# ============================================================================
# International — Japan national holidays
# ============================================================================

class TestJapanHolidays:
    """Japan national holidays using the 'japan' built-in calendar."""

    def test_japan_new_years_day_2025(self):
        """New Year's Day 2025 = Wednesday Jan 1."""
        assert is_holiday(date(2025, 1, 1), calendar="japan") is True
        assert get_holiday(date(2025, 1, 1), calendar="japan") == "New Year's Day (元日)"

    def test_japan_coming_of_age_day_2025(self):
        """Coming of Age Day 2025 = 2nd Monday in January = Jan 13."""
        assert is_holiday(date(2025, 1, 13), calendar="japan") is True
        assert get_holiday(date(2025, 1, 13), calendar="japan") == "Coming of Age Day (成人の日)"

    def test_japan_national_foundation_day_2025(self):
        """National Foundation Day 2025 = Tuesday Feb 11."""
        assert is_holiday(date(2025, 2, 11), calendar="japan") is True

    def test_japan_emperors_birthday_2025(self):
        """Emperor's Birthday 2025 = Sunday Feb 23 → observed Monday Feb 24."""
        assert is_holiday(date(2025, 2, 24), calendar="japan") is True
        assert get_holiday(date(2025, 2, 24), calendar="japan") == "Emperor's Birthday (天皇誕生日)"

    def test_japan_showa_day_2025(self):
        """Shōwa Day 2025 = Tuesday Apr 29."""
        assert is_holiday(date(2025, 4, 29), calendar="japan") is True

    def test_japan_golden_week_2025(self):
        """Golden Week: Constitution Day (May 3), Children's Day (May 5).

        Greenery Day (May 4) falls on Sunday in 2025 — observed shifts to
        Monday May 5, which overlaps with Children's Day. The engine resolves
        May 5 as Children's Day; May 4 (Sunday) is not an observed holiday.
        """
        assert is_holiday(date(2025, 5, 3), calendar="japan") is True
        assert is_holiday(date(2025, 5, 5), calendar="japan") is True
        # May 4 is Sunday — Greenery Day shifts to May 5 (overlap with Children's Day)
        assert is_holiday(date(2025, 5, 4), calendar="japan") is False

    def test_japan_marine_day_2025(self):
        """Marine Day 2025 = 3rd Monday in July = Jul 21."""
        assert is_holiday(date(2025, 7, 21), calendar="japan") is True
        assert get_holiday(date(2025, 7, 21), calendar="japan") == "Marine Day (海の日)"

    def test_japan_mountain_day_2025(self):
        """Mountain Day 2025 = Monday Aug 11."""
        assert is_holiday(date(2025, 8, 11), calendar="japan") is True

    def test_japan_respect_for_aged_day_2025(self):
        """Respect for the Aged Day 2025 = 3rd Monday in Sep = Sep 15."""
        assert is_holiday(date(2025, 9, 15), calendar="japan") is True

    def test_japan_sports_day_2025(self):
        """Sports Day 2025 = 2nd Monday in Oct = Oct 13."""
        assert is_holiday(date(2025, 10, 13), calendar="japan") is True
        assert get_holiday(date(2025, 10, 13), calendar="japan") == "Sports Day (スポーツの日)"

    def test_japan_culture_day_2025(self):
        """Culture Day 2025 = Monday Nov 3."""
        assert is_holiday(date(2025, 11, 3), calendar="japan") is True

    def test_japan_labour_thanksgiving_2025(self):
        """Labour Thanksgiving Day 2025 = Sunday Nov 23 → observed Monday Nov 24."""
        assert is_holiday(date(2025, 11, 24), calendar="japan") is True
        assert get_holiday(date(2025, 11, 24), calendar="japan") == "Labour Thanksgiving Day (勤労感謝の日)"

    def test_japan_holidays_2025_count(self):
        """Japan calendar has 14 holidays (excludes equinox-dependent)."""
        holidays = get_holidays(2025, calendar="japan")
        assert len(holidays) == 14

    def test_japan_us_holiday_not_in_japan(self):
        """US Thanksgiving (4th Thursday in Nov) is not a Japanese holiday."""
        assert is_holiday(date(2025, 11, 27), calendar="japan") is False

    def test_japan_emperor_birthday_before_2020(self):
        """Emperor's Birthday (Feb 23) was enacted in 2020 — 2019 should be False."""
        assert is_holiday(date(2019, 2, 23), calendar="japan") is False


# ============================================================================
# EASTER holidays — Good Friday & Easter Monday
# ============================================================================

class TestEasterHolidays:
    """EASTER rule type: holidays defined as an offset from Easter Sunday."""

    # Known Easter Sunday dates (independently verified):
    #   2024: Mar 31    2025: Apr 20    2026: Apr  5
    #   2027: Mar 28    2028: Apr 16

    # -- Good Friday (Easter − 2) -----------------------------------------------

    def test_good_friday_2024_uk(self):
        """Good Friday 2024 = Mar 29 (Easter Mar 31 − 2)."""
        assert is_holiday(date(2024, 3, 29), calendar="uk") is True
        assert get_holiday(date(2024, 3, 29), calendar="uk") == "Good Friday"

    def test_good_friday_2025_uk(self):
        """Good Friday 2025 = Apr 18 (Easter Apr 20 − 2)."""
        assert is_holiday(date(2025, 4, 18), calendar="uk") is True
        assert get_holiday(date(2025, 4, 18), calendar="uk") == "Good Friday"

    def test_good_friday_2026_uk(self):
        """Good Friday 2026 = Apr 3 (Easter Apr 5 − 2)."""
        assert is_holiday(date(2026, 4, 3), calendar="uk") is True

    def test_good_friday_2027_uk(self):
        """Good Friday 2027 = Mar 26 (Easter Mar 28 − 2)."""
        assert is_holiday(date(2027, 3, 26), calendar="uk") is True

    def test_good_friday_2028_uk(self):
        """Good Friday 2028 = Apr 14 (Easter Apr 16 − 2)."""
        assert is_holiday(date(2028, 4, 14), calendar="uk") is True

    # -- Easter Monday (Easter + 1) ---------------------------------------------

    def test_easter_monday_2024_uk(self):
        """Easter Monday 2024 = Apr 1 (Easter Mar 31 + 1)."""
        assert is_holiday(date(2024, 4, 1), calendar="uk") is True
        assert get_holiday(date(2024, 4, 1), calendar="uk") == "Easter Monday"

    def test_easter_monday_2025_uk(self):
        """Easter Monday 2025 = Apr 21 (Easter Apr 20 + 1)."""
        assert is_holiday(date(2025, 4, 21), calendar="uk") is True
        assert get_holiday(date(2025, 4, 21), calendar="uk") == "Easter Monday"

    def test_easter_monday_2026_uk(self):
        """Easter Monday 2026 = Apr 6 (Easter Apr 5 + 1)."""
        assert is_holiday(date(2026, 4, 6), calendar="uk") is True

    def test_easter_monday_2027_uk(self):
        """Easter Monday 2027 = Mar 29 (Easter Mar 28 + 1)."""
        assert is_holiday(date(2027, 3, 29), calendar="uk") is True

    def test_easter_monday_2028_uk(self):
        """Easter Monday 2028 = Apr 17 (Easter Apr 16 + 1)."""
        assert is_holiday(date(2028, 4, 17), calendar="uk") is True

    # -- Cross-calendar: same dates in Canada and banking -----------------------

    def test_good_friday_2025_canada(self):
        """Good Friday 2025 = Apr 18 on Canada calendar."""
        assert is_holiday(date(2025, 4, 18), calendar="canada") is True
        assert get_holiday(date(2025, 4, 18), calendar="canada") == "Good Friday"

    def test_easter_monday_2025_canada(self):
        """Easter Monday 2025 = Apr 21 on Canada calendar."""
        assert is_holiday(date(2025, 4, 21), calendar="canada") is True
        assert get_holiday(date(2025, 4, 21), calendar="canada") == "Easter Monday"

    def test_good_friday_2025_banking(self):
        """Good Friday 2025 = Apr 18 on US banking calendar."""
        assert is_holiday(date(2025, 4, 18), calendar="banking") is True
        assert get_holiday(date(2025, 4, 18), calendar="banking") == "Good Friday"

    def test_easter_monday_2025_banking(self):
        """Easter Monday 2025 = Apr 21 on US banking calendar."""
        assert is_holiday(date(2025, 4, 21), calendar="banking") is True
        assert get_holiday(date(2025, 4, 21), calendar="banking") == "Easter Monday"

    # -- Good Friday IS on the market calendar ------------------------------------

    def test_good_friday_on_market(self):
        """Good Friday is a NYSE/NASDAQ market holiday (since 1898)."""
        assert is_holiday(date(2025, 4, 18), calendar="market") is True
        assert get_holiday(date(2025, 4, 18), calendar="market") == "Good Friday"

    # -- Non-Easter dates are not holidays --------------------------------------

    def test_day_after_easter_monday_not_holiday(self):
        """The Tuesday after Easter is not a holiday."""
        assert is_holiday(date(2025, 4, 22), calendar="uk") is False

    def test_easter_sunday_not_a_holiday(self):
        """Easter Sunday itself is not defined as a bank holiday."""
        assert is_holiday(date(2025, 4, 20), calendar="uk") is False


# ============================================================================
# BEFORE holidays — Victoria Day (weekday on or before a date)
# ============================================================================

class TestVictoriaDay:
    """BEFORE rule type: Monday on or before May 24 (Canada)."""

    # May 24 weekday by year:
    #   2024: Friday   → Victoria Day = May 20 (Mon)
    #   2025: Saturday → Victoria Day = May 19 (Mon)
    #   2026: Sunday   → Victoria Day = May 18 (Mon)
    #   2027: Monday   → Victoria Day = May 24 (anchor IS Monday)
    #   2028: Wednesday→ Victoria Day = May 22 (Mon)

    def test_victoria_day_2024(self):
        """Victoria Day 2024 = May 20 (May 24 is Friday → previous Monday)."""
        assert is_holiday(date(2024, 5, 20), calendar="canada") is True
        assert get_holiday(date(2024, 5, 20), calendar="canada") == "Victoria Day"

    def test_victoria_day_2025(self):
        """Victoria Day 2025 = May 19 (May 24 is Saturday → previous Monday)."""
        assert is_holiday(date(2025, 5, 19), calendar="canada") is True
        assert get_holiday(date(2025, 5, 19), calendar="canada") == "Victoria Day"

    def test_victoria_day_2026(self):
        """Victoria Day 2026 = May 18 (May 24 is Sunday → previous Monday)."""
        assert is_holiday(date(2026, 5, 18), calendar="canada") is True

    def test_victoria_day_2027_anchor_is_monday(self):
        """Victoria Day 2027 = May 24 (anchor date IS Monday — zero offset)."""
        assert is_holiday(date(2027, 5, 24), calendar="canada") is True
        assert get_holiday(date(2027, 5, 24), calendar="canada") == "Victoria Day"

    def test_victoria_day_2028(self):
        """Victoria Day 2028 = May 22 (May 24 is Wednesday → previous Monday)."""
        assert is_holiday(date(2028, 5, 22), calendar="canada") is True

    def test_victoria_day_before_enactment(self):
        """Victoria Day was enacted in 1953 — 1952 should be False."""
        # In 1952, Monday on or before May 24 = May 19
        assert is_holiday(date(1952, 5, 19), calendar="canada") is False

    def test_victoria_day_not_on_uk(self):
        """Victoria Day is a Canadian holiday, not UK."""
        assert is_holiday(date(2025, 5, 19), calendar="uk") is False

    def test_may_24_not_always_victoria_day(self):
        """May 24 is NOT Victoria Day when it's not a Monday (2025: Saturday)."""
        assert get_holiday(date(2025, 5, 24), calendar="canada") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
