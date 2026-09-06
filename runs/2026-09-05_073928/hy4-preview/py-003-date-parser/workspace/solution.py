from __future__ import annotations

import re
from datetime import date

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

_MONTHS_ABBR = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

_ISO_RE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$")
_SLASH_RE = re.compile(r"^([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})$")
_FULL_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December)"
    r" ([0-9]{1,2}), ([0-9]{4})$",
    re.IGNORECASE,
)
_ABBR_RE = re.compile(
    r"^([0-9]{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ([0-9]{4})$",
    re.IGNORECASE,
)


def _to_iso(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()

    m = _ISO_RE.fullmatch(s)
    if m:
        year, month, day = map(int, m.groups())
        return _to_iso(year, month, day)

    m = _SLASH_RE.fullmatch(s)
    if m:
        day, month, year = map(int, m.groups())
        return _to_iso(year, month, day)

    m = _FULL_RE.fullmatch(s)
    if m:
        month_name, day, year = m.groups()
        month = _MONTHS_FULL[month_name.lower()]
        return _to_iso(int(year), month, int(day))

    m = _ABBR_RE.fullmatch(s)
    if m:
        day, month_name, year = m.groups()
        month = _MONTHS_ABBR[month_name.lower()]
        return _to_iso(int(year), month, int(day))

    return None
