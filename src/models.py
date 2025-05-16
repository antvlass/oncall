from datetime import timedelta, time, date
import holidays
from functools import lru_cache

from src.constants import DIV600_HOLIDAYS, DIV350_START_TIME


def _load_and_patch_year(year: int) -> dict[date, str]:
    base = {
        d: name for d, name in holidays.Sweden(years=year).items() if name != "Söndag"
    }

    injected = dict(base)
    for d, name in base.items():
        if "Långfredagen" in name:
            injected[d - timedelta(days=1)] = "Skärtorsdagen"
            injected[d + timedelta(days=1)] = "Påskafton"
        if "Pingstdagen" in name:
            injected[d - timedelta(days=1)] = "Pingstafton"

    return injected


class SwedishHolidays:
    def __init__(self, years: set[int]):
        all_holidays = {}
        for year in years:
            all_holidays.update(_load_and_patch_year(year))

        self.holiday_dict = all_holidays

        self.div600_holidays = {
            d
            for d, name in all_holidays.items()
            if any(tag in name for tag in DIV600_HOLIDAYS)
        }
        self.div350_holidays = {
            d for d, name in all_holidays.items() if d not in self.div600_holidays
        }

    def is_holiday(self, d: date) -> bool:
        return d in self.div600_holidays or d in self.div350_holidays

    def is_div600_holiday(self, d: date) -> bool:
        return d in self.div600_holidays

    def is_div350_holiday(self, d: date) -> bool:
        return d in self.div350_holidays

    def is_div350_start_day(self, d: date) -> bool:
        return d in self.div350_holidays or self.holiday_dict.get(d) == "Skärtorsdagen"

    @lru_cache
    def get_div350_start_time(self, d: date) -> time:
        return (
            time(18, 0)
            if self.holiday_dict.get(d) == "Skärtorsdagen"
            else DIV350_START_TIME
        )
