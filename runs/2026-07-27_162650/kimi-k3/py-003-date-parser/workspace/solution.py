"""Normalize date strings to ISO ``YYYY-MM-DD``."""

from __future__ import annotations

import re
from datetime import date

__all__ = ["normalize_date"]

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
_FULL_RE = re.compile(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})")
_ABBR_RE = re.compile(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})")


def _iso_or_none(year: int, month: int, day: int) -> str | None:
    """Return the ISO string for a date, or None if it is not a real date."""
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """Convert a supported date string to ISO ``YYYY-MM-DD``.

    Supported formats: ``2024-03-05``, ``05/03/2024``, ``March 5, 2024``
    and ``5 Mar 2024``. Returns ``None`` for anything that does not match
    one of these formats or is not a real calendar date.
    """
    if not isinstance(text, str):
        return None

    s = text.strip()

    m = _ISO_RE.fullmatch(s)
    if m:
        year, month, day = (int(g) for g in m.groups())
        return _iso_or_none(year, month, day)

    m = _SLASH_RE.fullmatch(s)
    if m:
        day, month, year = (int(g) for g in m.groups())
        return _iso_or_none(year, month, day)

    m = _FULL_RE.fullmatch(s)
    if m:
        month = _FULL_MONTHS.get(m.group(1).lower())
        if month is None:
            return None
        return _iso_or_none(int(m.group(3)), month, int(m.group(2)))

    m = _ABBR_RE.fullmatch(s)
    if m:
        month = _ABBR_MONTHS.get(m.group(2).lower())
        if month is None:
            return None
        return _iso_or_none(int(m.group(3)), month, int(m.group(1)))

    return None
