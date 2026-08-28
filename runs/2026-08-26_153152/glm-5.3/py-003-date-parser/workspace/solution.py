from __future__ import annotations

import re
from datetime import date

_FULL_MONTHS = {
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

_ABBR_MONTHS = {
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
_NAME_RE = re.compile(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})")
_ABBR_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})")


def _to_iso(year: int, month: int, day: int) -> str | None:
    """Return an ISO YYYY-MM-DD string, or None if not a real calendar date."""
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """Normalize a date string in one of four accepted formats to ISO YYYY-MM-DD.

    Accepted formats:
      1. YYYY-MM-DD      (already ISO)
      2. D/M/YYYY        (slashes; day/month zero-padded or not)
      3. Month D, YYYY   (full English month name, case-insensitive)
      4. D Mon YYYY      (3-letter English month abbreviation, case-insensitive)

    Surrounding whitespace is tolerated. Returns None for anything that does
    not match one of the four formats or is not a real calendar date.
    """
    if not isinstance(text, str):
        return None

    s = text.strip()

    # Format 1: already ISO.
    m = _ISO_RE.fullmatch(s)
    if m:
        return _to_iso(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # Format 2: day/month/year with slashes.
    m = _SLASH_RE.fullmatch(s)
    if m:
        return _to_iso(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    # Format 3: full month name, day, comma, 4-digit year.
    m = _NAME_RE.fullmatch(s)
    if m:
        month = _FULL_MONTHS.get(m.group(1).lower())
        if month is None:
            return None
        return _to_iso(int(m.group(3)), month, int(m.group(2)))

    # Format 4: day, 3-letter month abbreviation, 4-digit year.
    m = _ABBR_RE.fullmatch(s)
    if m:
        month = _ABBR_MONTHS.get(m.group(2).lower())
        if month is None:
            return None
        return _to_iso(int(m.group(3)), month, int(m.group(1)))

    return None
