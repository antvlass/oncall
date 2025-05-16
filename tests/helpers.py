from datetime import date, time


class MockCalendar:
    def __init__(
        self,
        *,
        div600: set = None,
        div350: set = None,
        holiday_dict: dict[date, str] = None
    ):
        self.div600 = div600 or set()
        self.div350 = div350 or set()
        self.holiday_dict = holiday_dict or {}

    def is_div600_holiday(self, d: date) -> bool:
        return d in self.div600

    def is_div350_holiday(self, d: date) -> bool:
        return d in self.div350

    def is_div350_start_day(self, d: date) -> bool:
        return d in self.div350 or self.holiday_dict.get(d) == "Skärtorsdagen"

    def is_holiday(self, d: date) -> bool:
        return self.is_div600_holiday(d) or self.is_div350_holiday(d)

    def get_div350_start_time(self, d: date) -> time:
        return (
            time(18, 0) if self.holiday_dict.get(d) == "Skärtorsdagen" else time(7, 0)
        )
