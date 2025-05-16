from datetime import date

from src.constants import Category


def print_day_output(day: date, hours: dict[Category, int]):
    for category in Category.list():
        if hours.get(category):
            print(f"{day}: {category.value:<7} = {hours[category]:>2}")


def print_summary(total: dict[Category, int]):
    print("\n== Summary ==")
    for category in Category.list():
        if total.get(category):
            print(f"{category.value:<7} = {total[category]:>2}")


def print_compensation(total: dict[Category, int], salary: float):
    total_amount = sum(
        (salary / category.get_divisor()) * total.get(category, 0)
        for category in Category.list()
    )
    print(f"\n{'Extra':<5} = {total_amount:>8.2f} kr")
    print(f"{'Total':<5} = {salary + total_amount:>8.2f} kr")
