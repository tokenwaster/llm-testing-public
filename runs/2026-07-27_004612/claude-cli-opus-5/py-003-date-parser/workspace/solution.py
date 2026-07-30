"""Normalize dates from four common formats to ISO YYYY-MM-DD."""

import re
from datetime import date

MONTHS = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]

FULL_MONTHS = {name: i for i, name in enumerate(MONTHS, start=1)}
ABBR_MONTHS = {name[:3]: i for i, name in enumerate(MONTHS, start=1)}

ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
FULL_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")
ABBR_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")


def _build(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """Convert a date string in one of four supported formats to ISO format.

    Returns None if the text does not match a supported format or does not
    denote a real calendar date.
    """
    if not isinstance(text, str):
        return None

    s = text.strip()
    if not s:
        return None

    m = ISO_RE.match(s)
    if m:
        return _build(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = SLASH_RE.match(s)
    if m:
        return _build(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = FULL_RE.match(s)
    if m:
        month = FULL_MONTHS.get(m.group(1).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(2)))

    m = ABBR_RE.match(s)
    if m:
        month = ABBR_MONTHS.get(m.group(2).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(1)))

    return None
