"""solution.py — Normalize common date string formats to ISO 8601 (YYYY-MM-DD)."""

from __future__ import annotations

import re
from datetime import date

# --- Compiled patterns for each supported format ---------------------------

# 1. ISO: YYYY-MM-DD (strictly zero-padded)
_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

# 2. Slashes: D/M/YYYY (zero-padding optional)
_SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")

# 3. Full English month name: "Month D, YYYY" (comma required)
_NAME_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2})\s*,\s*(\d{4})$")

# 4. 3-letter month abbreviation: "D Mon YYYY"
_ABBR_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")

# --- Month lookup tables ----------------------------------------------------

_MONTH_NAMES = {
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

_MONTH_ABBRS = {
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


def _build(year: int, month: int, day: int) -> str | None:
    """Return the ISO string for (year, month, day), or None if not a real date."""
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """Convert *text* in one of four supported formats to ``YYYY-MM-DD``.

    Supported formats:
      1. ``YYYY-MM-DD``     -- already ISO; validated and returned as-is
      2. ``D/M/YYYY``       -- slashes, zero-padding optional
      3. ``Month D, YYYY``  -- full English month name, comma required
      4. ``D Mon YYYY``     -- 3-letter English month abbreviation

    Surrounding whitespace is tolerated and month names are matched
    case-insensitively. Returns ``None`` for anything that does not match
    one of the formats or is not a real calendar date.
    """
    if not isinstance(text, str):
        return None

    s = text.strip()

    # 1. ISO: YYYY-MM-DD
    m = _ISO_RE.match(s)
    if m:
        return _build(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # 2. Slashes: D/M/YYYY
    m = _SLASH_RE.match(s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _build(year, month, day)

    # 3. Full month name: Month D, YYYY
    m = _NAME_RE.match(s)
    if m:
        month = _MONTH_NAMES.get(m.group(1).lower())
        if month is not None:
            return _build(int(m.group(3)), month, int(m.group(2)))

    # 4. Abbreviation: D Mon YYYY
    m = _ABBR_RE.match(s)
    if m:
        month = _MONTH_ABBRS.get(m.group(2).lower())
        if month is not None:
            return _build(int(m.group(3)), month, int(m.group(1)))

    return None
