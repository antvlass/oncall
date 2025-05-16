import pytest
from datetime import date, time
from src.constants import Category
from src.engine import OnCallClassifier, DayState
from tests.helpers import MockCalendar


# fmt: off
@pytest.mark.parametrize("today, state, hour, weekday, calendar_kwargs, expected", [
    # HOLIDAY600_EXTENSION
    (date(2030, 1, 1), DayState.HOLIDAY600_EXTENSION, 6, 5, {}, Category.DIV600),
    (date(2030, 1, 1), DayState.HOLIDAY600_EXTENSION, 7, 5, {"div350": {date(2030, 1, 1)}}, Category.DIV350),

    # HOLIDAY600_EXTENSION on Skärtorsdagen
    (date(2030, 4, 17), DayState.HOLIDAY600_EXTENSION, 17, 3, {"div350": {date(2030, 4, 17)}, "holiday_dict": {date(2030, 4, 17): "Skärtorsdagen"}}, Category.DIV600),
    (date(2030, 4, 17), DayState.HOLIDAY600_EXTENSION, 18, 3, {"div350": {date(2030, 4, 17)}, "holiday_dict": {date(2030, 4, 17): "Skärtorsdagen"}}, Category.DIV350),

    # HOLIDAY350_START
    (date(2030, 1, 2), DayState.HOLIDAY350_START, 8, 3, {"div350": {date(2030, 1, 2)}}, Category.DIV350),
    (date(2030, 1, 2), DayState.HOLIDAY350_START, 6, 3, {"div350": {date(2030, 1, 2)}}, Category.DIV1400),
    (date(2030, 1, 2), DayState.HOLIDAY350_START, 6, 5, {"div350": {date(2030, 1, 2)}}, Category.DIV600),

    # HOLIDAY350_START on Skärtorsdagen
    (date(2030, 4, 17), DayState.HOLIDAY350_START, 14, 3, {"div350": {date(2030, 4, 17)}, "holiday_dict": {date(2030, 4, 17): "Skärtorsdagen"}}, None),
    (date(2030, 4, 17), DayState.HOLIDAY350_START, 17, 3, {"div350": {date(2030, 4, 17)}, "holiday_dict": {date(2030, 4, 17): "Skärtorsdagen"}}, Category.DIV1400),
    (date(2030, 4, 17), DayState.HOLIDAY350_START, 18, 3, {"div350": {date(2030, 4, 17)}, "holiday_dict": {date(2030, 4, 17): "Skärtorsdagen"}}, Category.DIV350),

    # HOLIDAY350_EXTENSION
    (date(2030, 1, 3), DayState.HOLIDAY350_EXTENSION, 12, 4, {}, Category.DIV350),

    # HOLIDAY600
    (date(2030, 1, 4), DayState.HOLIDAY600, 6, 5, {}, Category.DIV900),
    (date(2030, 1, 4), DayState.HOLIDAY600, 8, 5, {}, Category.DIV600),

    # PRE_HOLIDAY600
    (date(2030, 1, 5), DayState.PRE_HOLIDAY600, 6, 3, {}, Category.DIV1400),
    (date(2030, 1, 5), DayState.PRE_HOLIDAY600, 18, 3, {}, Category.DIV900),

    # NORMAL Friday
    (date(2030, 1, 6), DayState.NORMAL, 6, 4, {}, Category.DIV1400),
    (date(2030, 1, 6), DayState.NORMAL, 17, 4, {}, Category.DIV1400),
    (date(2030, 1, 6), DayState.NORMAL, 18, 4, {}, Category.DIV900),

    # NORMAL Saturday
    (date(2030, 1, 7), DayState.NORMAL, 6, 5, {}, Category.DIV900),
    (date(2030, 1, 7), DayState.NORMAL, 8, 5, {}, Category.DIV600),

    # NORMAL Sunday
    (date(2030, 1, 8), DayState.NORMAL, 10, 6, {}, Category.DIV600),

    # NORMAL Weekday outside work
    (date(2030, 1, 9), DayState.NORMAL, 6, 2, {}, Category.DIV1400),
    (date(2030, 1, 9), DayState.NORMAL, 14, 2, {}, None),
])
def test_categorize_by_state(today, state, hour, weekday, calendar_kwargs, expected):
    cal = MockCalendar(**calendar_kwargs)
    classifier = OnCallClassifier(cal, today)
    classifier.state = state
    classifier.today = today
    classifier.weekday = weekday

    result = classifier.categorize(time(hour))

    assert result == expected, (
        f"{today} hour {hour}: expected {expected}, got {result}, "
        f"state={state}, weekday={weekday}, cal_kwargs={calendar_kwargs}"
    )
