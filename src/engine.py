from datetime import datetime, timedelta, time, date
from enum import Enum, auto
from functools import lru_cache

from src.constants import (
    Category,
    WORK_START,
    WORK_END,
    DIV900_START,
    DIV900_END,
)
from src.models import SwedishHolidays


class DayState(Enum):
    NORMAL = auto()
    PRE_HOLIDAY600 = auto()
    HOLIDAY600 = auto()
    HOLIDAY600_EXTENSION = auto()
    HOLIDAY350_START = auto()
    HOLIDAY350_EXTENSION = auto()


def is_working_day(d: date, cal: SwedishHolidays) -> bool:
    return d.weekday() < 5 and not cal.is_holiday(d)


def is_outside_working_hours(t: time, weekday: int) -> bool:
    return weekday >= 5 or t < WORK_START or t >= WORK_END


def daterange(start: date, end: date):
    for n in range((end - start).days + 1):
        yield start + timedelta(days=n)


def get_category_eve(t: time) -> Category | None:
    if t < WORK_START or (WORK_END <= t < DIV900_START):
        return Category.DIV1400
    if t >= DIV900_START:
        return Category.DIV900
    return None


class OnCallClassifier:
    def __init__(self, cal: SwedishHolidays, start_date: date):
        self.cal = cal
        self.prev_state: DayState = DayState.NORMAL
        self.state: DayState | None = None
        self.weekday: int | None = None
        self.today: date | None = None

        self._initialize_state(start_date)

    def _initialize_state(self, start_date) -> None:
        scan_day = start_date - timedelta(days=1)
        while not is_working_day(scan_day, self.cal):
            scan_day -= timedelta(days=1)

        state = DayState.NORMAL
        while scan_day < start_date:
            state = self._compute_state(scan_day, state)
            scan_day += timedelta(days=1)

        self.prev_state = state

    def _get_normal_day_category(self, t: time) -> Category | None:
        if self.weekday == 4:
            return get_category_eve(t)

        elif self.weekday == 5:
            return Category.DIV900 if t < DIV900_END else Category.DIV600

        elif self.weekday == 6:
            return Category.DIV600

        elif is_outside_working_hours(t, self.weekday):
            return Category.DIV1400

        return None

    @lru_cache
    def _compute_state(self, today: date, yesterday_state: DayState) -> DayState:
        is_working = is_working_day(today, self.cal)
        is_holiday600 = self.cal.is_div600_holiday(today)
        is_holiday350 = self.cal.is_div350_start_day(today)
        is_pre_holiday600 = self.cal.is_div600_holiday(today + timedelta(days=1))

        if yesterday_state in {
            DayState.HOLIDAY350_START,
            DayState.HOLIDAY350_EXTENSION,
        }:
            if not is_working:
                return DayState.HOLIDAY350_EXTENSION

        if yesterday_state in {DayState.HOLIDAY600, DayState.HOLIDAY600_EXTENSION}:
            if not is_working and not is_holiday350:
                return DayState.HOLIDAY600_EXTENSION

        if is_holiday350:
            return DayState.HOLIDAY350_START

        if is_holiday600:
            return DayState.HOLIDAY600

        if is_pre_holiday600:
            return DayState.PRE_HOLIDAY600

        return DayState.NORMAL

    def begin_day(self, d: date) -> None:
        self.today = d
        self.weekday = d.weekday()
        self.state = self._compute_state(d, self.prev_state)

    def categorize(self, t: time) -> Category | None:
        if self.state is None or self.today is None or self.weekday is None:
            raise ValueError("Call `begin_day(date)` before `categorize()`")

        match self.state:
            case DayState.HOLIDAY600_EXTENSION:
                if self.cal.is_div350_holiday(self.today):
                    start_time = self.cal.get_div350_start_time(self.today)
                    return Category.DIV600 if t < start_time else Category.DIV350
                return Category.DIV600

            case DayState.HOLIDAY350_START:
                start_time = self.cal.get_div350_start_time(self.today)
                if t >= start_time:
                    return Category.DIV350
                if self.weekday == 5 and t < start_time:
                    return Category.DIV600
                if self.weekday < 5 and is_outside_working_hours(t, self.weekday):
                    return Category.DIV1400
                return None

            case DayState.HOLIDAY350_EXTENSION:
                return Category.DIV350

            case DayState.HOLIDAY600:
                return Category.DIV900 if t < DIV900_END else Category.DIV600

            case DayState.PRE_HOLIDAY600:
                return get_category_eve(t)

            case DayState.NORMAL:
                return self._get_normal_day_category(t)

        return None


def run_oncall_block(
    start_dt: datetime, end_dt: datetime, cal: SwedishHolidays
) -> dict:
    start_date, end_date = start_dt.date(), end_dt.date()
    classifier = OnCallClassifier(cal, start_date)

    total = {}
    for day in daterange(start_date, end_date):
        classifier.begin_day(day)

        hours = {k: 0 for k in Category.list()}
        for hour in range(24):
            t = time(hour)
            if day == start_date and t < start_dt.time():
                continue
            if day == end_date and t >= end_dt.time():
                continue

            cat = classifier.categorize(t)
            if cat:
                hours[cat] += 1

        total[day] = hours
        classifier.prev_state = classifier.state

    return total
