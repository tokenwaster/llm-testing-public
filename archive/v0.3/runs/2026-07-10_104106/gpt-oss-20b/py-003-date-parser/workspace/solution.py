#!/usr/bin/env python3
"""
normalize_date.py

Provides a single function `normalize_date(text: str) -> str | None` that converts
dates in four specific formats to ISO 8601 format (YYYY-MM-DD). If the input does
not match any of the supported formats or represents an invalid calendar date,
the function returns None.
"""

import re
from datetime import date

# Mapping of month names and abbreviations to month numbers
_MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

# Regular expressions for the four supported formats
_RE_ISO = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
_RE_DMY_SLASH = re.compile(
    r"^\s*(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})\s*$"
)
_RE_FULL_MONTH = re.compile(
    r"^\s*(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\s*$",
    re.IGNORECASE,
)
_RE_ABBR_MONTH = re.compile(
    r"^\s*(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]{3})\s+(?P<year>\d{4})\s*$",
    re.IGNORECASE,
)


def _validate_and_format(year: int, month: int, day: int) -> str | None:
    """Validate the date components and return ISO string if valid."""
    try:
        d = date(year, month, day)
    except ValueError:
        return None
    return d.isoformat()


def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four supported formats to ISO 8601 format.

    Supported input formats:
      1. "YYYY-MM-DD" (ISO, may have surrounding whitespace)
      2. "DD/MM/YYYY" or "D/M/YYYY" (day/month/year with slashes)
      3. "MonthName D, YYYY" (full month name, comma after day)
      4. "D Mon YYYY" (three-letter month abbreviation)

    Parameters
    ----------
    text : str
        The input date string.

    Returns
    -------
    str | None
        ISO formatted date string ("YYYY-MM-DD") if the input is valid,
        otherwise None.
    """
    # 1. ISO format
    m = _RE_ISO.match(text)
    if m:
        year, month, day = map(int, m.groups())
        return _validate_and_format(year, month, day)

    # 2. Day/Month/Year with slashes
    m = _RE_DMY_SLASH.match(text)
    if m:
        day = int(m.group("day"))
        month = int(m.group("month"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 3. Full month name
    m = _RE_FULL_MONTH.match(text)
    if m:
        month_name = m.group("month").lower()
        month = _MONTH_MAP.get(month_name)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 4. Abbreviated month name
    m = _RE_ABBR_MONTH.match(text)
    if m:
        month_abbr = m.group("month").lower()
        month = _MONTH_MAP.get(month_abbr)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # No pattern matched
    return None


# If run as a script, perform simple tests
if __name__ == "__main__":
    test_cases = [
        "2024-03-05",
        "  2024-3-5  ",
        "05/03/2024",
        "5/3/2024",
        "March 5, 2024",
        "march 5, 2024",
        "5 Mar 2024",
        "31/02/2024",   # invalid
        "Feb 29, 2021", # invalid (non-leap year)
    ]
    for tc in test_cases:
        print(f"{tc!r} -> {normalize_date(tc)!r}")
