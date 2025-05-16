from collections import defaultdict
from datetime import date

from src.cli import (
    parse_args,
    parse_range_string,
    load_ranges_from_file,
    get_pagerduty_ranges,
)
from src.models import SwedishHolidays
from src.constants import Category
from src.engine import run_oncall_block
from src.output import print_summary, print_compensation, print_day_output


def compute_totals(all_days: dict[date, dict[Category, int]]) -> dict[Category, int]:
    total = defaultdict(int)

    for hours in all_days.values():
        for category, value in hours.items():
            total[category] += value

    return dict(total)


def main():
    args = parse_args()

    if args.range_file:
        ranges = load_ranges_from_file(args.range_file)
    elif args.pagerduty and args.month:
        ranges = get_pagerduty_ranges(args.pagerduty, args.month)
    elif args.range:
        ranges = [parse_range_string(r) for r in args.range]
    else:
        raise ValueError("Use --range, --pagerduty + --month, or --range-file.")

    all_blocks = {}

    print("== Details ==")
    for start_dt, end_dt in ranges:
        years = {start_dt.year, end_dt.year}
        cal = SwedishHolidays(years)
        block_total = run_oncall_block(start_dt, end_dt, cal)
        for day, hours in block_total.items():
            all_blocks[day] = hours
            print_day_output(day, hours)

    total = compute_totals(all_blocks)
    print_summary(total)

    if args.salary:
        print_compensation(total, args.salary)


if __name__ == "__main__":
    main()
