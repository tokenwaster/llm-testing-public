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

_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_SLASH = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_FULL = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")
_ABBR = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")


def _iso_or_none(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    s = text.strip()

    m = _ISO.fullmatch(s)
    if m:
        return _iso_or_none(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = _SLASH.fullmatch(s)
    if m:
        return _iso_or_none(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = _FULL.fullmatch(s)
    if m:
        month = _MONTHS_FULL.get(m.group(1).lower())
        if month is None:
            return None
        return _iso_or_none(int(m.group(3)), month, int(m.group(2)))

    m = _ABBR.fullmatch(s)
    if m:
        month = _MONTHS_ABBR.get(m.group(2).lower())
        if month is None:
            return None
        return _iso_or_none(int(m.group(3)), month, int(m.group(1)))

    return None
