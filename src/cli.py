import argparse
import re
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

RANGE_PATTERN = re.compile(r"^(.*?)\s+to\s+(.*?)$")

LOCAL_TZ = ZoneInfo("Europe/Stockholm")
UTC_TZ = ZoneInfo("UTC")

PD_HOST = "https://api.pagerduty.com"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pagerduty", help="PagerDuty API token", type=str)
    parser.add_argument("--month", help="Month in YYYYMM", type=str)
    parser.add_argument("--range", action="append")
    parser.add_argument("--range-file")
    parser.add_argument("--salary", type=int, default=None)
    return parser.parse_args()


def parse_range_string(r: str) -> tuple[datetime, datetime]:
    m = RANGE_PATTERN.match(r.strip())
    if not m:
        raise ValueError(f"Invalid range format: {r}")
    fmt = "%Y-%m-%d %H:%M" if ":" in r else "%Y-%m-%d"
    return datetime.strptime(m.group(1), fmt), datetime.strptime(m.group(2), fmt)


def to_local(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(LOCAL_TZ)


def to_utc_iso(dt: datetime) -> str:
    return dt.astimezone(UTC_TZ).isoformat().replace("+00:00", "Z")


def get_pagerduty_ranges(token: str, month: str) -> list[tuple[datetime, datetime]]:
    if not re.fullmatch(r"\d{6}", month):
        raise ValueError(f"Invalid --month format: {month}. Expected YYYYMM.")

    month_start = datetime.strptime(month, "%Y%m").replace(tzinfo=LOCAL_TZ)
    month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)

    headers = {
        "Authorization": f"Token token={token}",
        "Accept": "application/vnd.pagerduty+json;version=2",
    }

    user_resp = requests.get(f"{PD_HOST}/users/me", headers=headers)
    user_resp.raise_for_status()
    user_id = user_resp.json()["user"]["id"]

    params = {
        "user_ids[]": user_id,
        "since": to_utc_iso(month_start),
        "until": to_utc_iso(month_end),
    }
    response = requests.get(f"{PD_HOST}/oncalls", headers=headers, params=params)
    response.raise_for_status()

    ranges = []
    for entry in response.json().get("oncalls", []):
        start = to_local(entry["start"])
        end = to_local(entry["end"])

        clipped_start = max(start, month_start)
        clipped_end = min(end, month_end)

        if clipped_start < clipped_end:
            ranges.append((clipped_start, clipped_end))

    return ranges


def load_ranges_from_file(path: str) -> list[tuple[datetime, datetime]]:
    with open(path) as f:
        return [parse_range_string(line) for line in f if line.strip()]
