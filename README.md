# Calculate oncall hours

Install dependencies using Poetry.

```bash
poetry install
```

Get the oncall hours from a given time range.
```bash
poetry run python main.py --range "2025-04-05 08:00 to 2025-04-06 08:00"
```

Get the oncall hours from a given file containing a list of time ranges.
```bash
poetry run python main.py --range-file "oncall_may.txt"
```

Get the oncall hours from PagerDuty with personal API User-Token (to create in your User Settings).
```bash
poetry run python main.py --pagerduty <USER-TOKEN> --month "202505"  
```

Get compensation information based on salary
```bash
poetry run python main.py --range "2025-04-05 08:00 to 2025-04-06 08:00" --salary 100000
```