from __future__ import annotations

import re
from datetime import date

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_FULL_MONTH_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")
_ABBR_MONTH_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")

_MONTHS_FULL = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

_MONTHS_ABBR = {name[:3]: number for name, number in _MONTHS_FULL.items()}


def _to_iso(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()

    match = _ISO_RE.match(s)
    if match:
        year, month, day = map(int, match.groups())
        return _to_iso(year, month, day)

    match = _SLASH_RE.match(s)
    if match:
        day, month, year = map(int, match.groups())
        return _to_iso(year, month, day)

    match = _FULL_MONTH_RE.match(s)
    if match:
        month_name, day_s, year_s = match.groups()
        month = _MONTHS_FULL.get(month_name.lower())
        if month is None:
            return None
        return _to_iso(int(year_s), month, int(day_s))

    match = _ABBR_MONTH_RE.match(s)
    if match:
        day_s, abbr, year_s = match.groups()
        month = _MONTHS_ABBR.get(abbr.lower())
        if month is None:
            return None
        return _to_iso(int(year_s), month, int(day_s))

    return None
