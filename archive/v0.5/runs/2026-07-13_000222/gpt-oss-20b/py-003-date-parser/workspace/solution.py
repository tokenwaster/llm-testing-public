#!/usr/bin/env python3
"""
normalize_date module

Provides a single function `normalize_date(text: str) -> str | None`
that normalises dates in four specific formats to ISO YYYY-MM-DD.
"""

import re
from datetime import date
from typing import Optional

# Mapping of month names and abbreviations (case-insensitive)
MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

# Regular expressions for the four supported formats
ISO_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
DMY_SLASH_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})\s*$"
)
MONTH_NAME_RE = re.compile(
    r"^\s*(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\s*$",
    re.IGNORECASE,
)
DAY_ABBR_MONTH_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]{3})\s+(?P<year>\d{4})\s*$",
    re.IGNORECASE,
)


def _validate_and_format(year: int, month: int, day: int) -> Optional[str]:
    """Validate the date components and return ISO string if valid."""
    try:
        d = date(year, month, day)
    except ValueError:
        return None
    return d.isoformat()


def normalize_date(text: str) -> Optional[str]:
    """
    Convert a date string in one of four supported formats to ISO YYYY-MM-DD.

    Parameters
    ----------
    text : str
        Input date string.

    Returns
    -------
    Optional[str]
        ISO formatted date or None if the input is invalid.
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
        month = MONTH_MAP.get(month_abbr)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # No format matched
    return None

# If run as a script, provide simple tests
if __name__ == "__main__":
    test_cases = [
        ("2024-03-05", "2024-03-05"),
        (" 5/3/2024 ", "2024-03-05"),
        ("March 5, 2024", "2024-03-05"),
        ("5 Mar 2024", "2024-03-05"),
        ("31/02/2024", None),
        ("Feb 29, 2023", None),  # not a leap year
    ]

    for inp, expected in test_cases:
        result = normalize_date(inp)
        print(f"{inp!r} -> {result!r} (expected: {expected!r})")
