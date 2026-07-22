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

_ISO_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_SLASH_RE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_FULL_RE = re.compile(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})")
_ABBR_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})")


def _to_iso(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """Convert a date string in a supported format to ISO ``YYYY-MM-DD``.

    Returns ``None`` if the input matches none of the supported formats
    or does not represent a real calendar date.
    """
    if not isinstance(text, str):
        return None

    s = text.strip()

    # 1. ISO: YYYY-MM-DD
    m = _ISO_RE.fullmatch(s)
    if m:
        year, month, day = (int(g) for g in m.groups())
        return _to_iso(year, month, day)

    # 2. day/month/year with slashes
    m = _SLASH_RE.fullmatch(s)
    if m:
        day, month, year = (int(g) for g in m.groups())
        return _to_iso(year, month, day)

    # 3. Full month name: "March 5, 2024"
    m = _FULL_RE.fullmatch(s)
    if m:
        name, day, year = m.groups()
        month = _MONTHS_FULL.get(name.lower())
        if month is None:
            return None
        return _to_iso(int(year), month, int(day))

    # 4. 3-letter month abbreviation: "5 Mar 2024"
    m = _ABBR_RE.fullmatch(s)
    if m:
        day, abbr, year = m.groups()
        month = _MONTHS_ABBR.get(abbr.lower())
        if month is None:
            return None
        return _to_iso(int(year), month, int(day))

    return None
