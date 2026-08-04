"""Normalize date strings in several common formats to ISO ``YYYY-MM-DD``."""

from __future__ import annotations

import re
from datetime import date

__all__ = ["normalize_date"]

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

# Full month name -> month number (lower-cased keys)
_FULL_MONTHS = {name.lower(): i for i, name in enumerate(_MONTH_NAMES, start=1)}

# 3-letter abbreviation -> month number (lower-cased keys)
_ABBR_MONTHS = {name[:3].lower(): i for i, name in enumerate(_MONTH_NAMES, start=1)}

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_FULL_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2})\s*,\s*(\d{4})$")
_ABBR_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")


def _build(year: int, month: int, day: int) -> str | None:
    """Return the ISO string for the given components, or None if invalid."""
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """Convert a date string to ISO ``YYYY-MM-DD`` form.

    Recognized inputs (surrounding whitespace tolerated, month names
    case-insensitive):

    * ``"2024-03-05"``   -- already ISO
    * ``"05/03/2024"``   -- day/month/year, zero padding optional
    * ``"March 5, 2024"`` -- full English month name
    * ``"5 Mar 2024"``   -- 3-letter English month abbreviation

    Returns ``None`` when the input does not match one of these formats or does
    not denote a real calendar date.
    """
    if not isinstance(text, str):
        return None

    s = text.strip()
    if not s:
        return None

    m = _ISO_RE.match(s)
    if m:
        year, month, day = (int(g) for g in m.groups())
        return _build(year, month, day)

    m = _SLASH_RE.match(s)
    if m:
        day, month, year = (int(g) for g in m.groups())
        return _build(year, month, day)

    m = _FULL_RE.match(s)
    if m:
        month = _FULL_MONTHS.get(m.group(1).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(2)))

    m = _ABBR_RE.match(s)
    if m:
        month = _ABBR_MONTHS.get(m.group(2).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(1)))

    return None
