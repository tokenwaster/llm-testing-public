# solution.py

import re
from datetime import date


MONTH_MAP = {
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

ABBR_MAP = {k[:3]: v for k, v in MONTH_MAP.items()}


# Regular expressions for the four formats
ISO_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
DMY_SLASH_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})\s*$"
)
MONTH_NAME_RE = re.compile(
    r"^\s*(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\s*$"
)
DAY_ABBR_MONTH_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]{3})\s+(?P<year>\d{4})\s*$"
)


def _validate_and_format(year: int, month: int, day: int) -> str | None:
    """Return ISO string if the date is valid, otherwise None."""
    try:
        d = date(year, month, day)
        return d.isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four supported formats to ISO YYYY-MM-DD.
    Return None if the input does not match any format or is not a real date.
    """
    # 1. ISO format
    m = ISO_RE.match(text)
    if m:
        year, month, day = map(int, m.groups())
        return _validate_and_format(year, month, day)

    # 2. DD/MM/YYYY with slashes
    m = DMY_SLASH_RE.match(text)
    if m:
        day = int(m.group("day"))
        month = int(m.group("month"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 3. Full month name
    m = MONTH_NAME_RE.match(text)
    if m:
        month_name = m.group("month").lower()
        month = MONTH_MAP.get(month_name)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 4. Day + 3-letter abbreviation
    m = DAY_ABBR_MONTH_RE.match(text)
    if m:
        month_abbr = m.group("month").lower()
        month = ABBR_MAP.get(month_abbr)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # No pattern matched
    return None
