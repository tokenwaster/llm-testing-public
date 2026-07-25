"""Normalize dates in several common formats to ISO ``YYYY-MM-DD``."""

import re
from datetime import date

MONTH_NAMES = {
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

MONTH_ABBRS = {name[:3]: number for name, number in MONTH_NAMES.items()}

ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
MONTH_FIRST_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")
DAY_FIRST_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")


def _build(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """Return ``text`` as an ISO date string, or ``None`` if it isn't a valid date.

    Accepted inputs: ``2024-03-05``, ``05/03/2024`` (day/month/year),
    ``March 5, 2024`` and ``5 Mar 2024``.
    """
    if not isinstance(text, str):
        return None

    candidate = text.strip()

    match = ISO_RE.match(candidate)
    if match:
        year, month, day = (int(part) for part in match.groups())
        return _build(year, month, day)

    match = SLASH_RE.match(candidate)
    if match:
        day, month, year = (int(part) for part in match.groups())
        return _build(year, month, day)

    match = MONTH_FIRST_RE.match(candidate)
    if match:
        name, day, year = match.groups()
        month = MONTH_NAMES.get(name.lower())
        if month is None:
            return None
        return _build(int(year), month, int(day))

    match = DAY_FIRST_RE.match(candidate)
    if match:
        day, abbr, year = match.groups()
        month = MONTH_ABBRS.get(abbr.lower())
        if month is None:
            return None
        return _build(int(year), month, int(day))

    return None
