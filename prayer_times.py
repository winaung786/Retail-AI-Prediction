#!/usr/bin/env python3
"""Retrieve and display prayer times for a given location.

This script fetches prayer times from the Aladhan API (https://aladhan.com/)
and prints them in a simple table along with a motivational quote from Mufti
Menk. A working internet connection is required to fetch the latest times.
"""

import json
import sys
from dataclasses import dataclass
from datetime import date
from urllib.request import urlopen, Request
from urllib.error import URLError

MUFTI_MENK_QUOTE = (
    "Mufti Menk reminds us: 'Never underestimate the power of a sincere prayer. "
    "Keep calling out to the Almighty. He hears you.'"
)

@dataclass
class Location:
    latitude: float
    longitude: float
    timezone: float

API_URL = "https://api.aladhan.com/v1/timings/{date}?latitude={lat}&longitude={lon}&timezonestring=UTC{tz:+}"  # noqa: E501


def fetch_prayer_times(location: Location, date_str: str) -> dict:
    url = API_URL.format(date=date_str, lat=location.latitude, lon=location.longitude, tz=location.timezone)
    try:
        with urlopen(Request(url, headers={"User-Agent": "prayer-times-script"})) as resp:
            data = json.load(resp)
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch prayer times: {exc}") from exc
    return data["data"]["timings"]


def print_prayer_times(times: dict, loc: Location, date_str: str) -> None:
    print(f"Prayer times for {date_str} at ({loc.latitude}, {loc.longitude}) UTC{loc.timezone:+}")
    for key in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        print(f"{key:8s}: {times[key]}")
    print("\n" + MUFTI_MENK_QUOTE)


def main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Display prayer times from Aladhan API")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--tz", type=float, required=True, help="UTC offset, e.g. 3 for UTC+3")
    parser.add_argument("--date", type=str, default=date.today().isoformat(), help="YYYY-MM-DD")

    args = parser.parse_args(argv)
    loc = Location(args.lat, args.lon, args.tz)

    try:
        times = fetch_prayer_times(loc, args.date)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    print_prayer_times(times, loc, args.date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
