#!/usr/bin/env python3
"""
Solution to normalize_date problem.
"""

import re
from datetime import date

# Mapping of month names and abbreviations to month numbers
MONTH_MAP = {
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
    "december": 12, "dec": 12
}

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
    """Validate the date and return ISO string if valid."""
    try:
        d = date(year, month, day)
    except ValueError:
        return None
    return d.isoformat()

def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four supported formats to ISO YYYY-MM-DD.
    Return None if the input does not match any format or is not a valid date.
    """
    # Try ISO format first (validate)
    m = ISO_RE.match(text)
    if m:
        year, month, day = map(int, m.groups())
        return _validate_and_format(year, month, day)

    # Day/Month/Year with slashes
    m = DMY_SLASH_RE.match(text)
    if m:
        day = int(m.group('day'))
        month = int(m.group('month'))
        year = int(m.group('year'))
        return _validate_and_format(year, month, day)

    # Full month name
    m = MONTH_NAME_RE.match(text)
    if m:
        month_name = m.group('month').lower()
        month = MONTH_MAP.get(month_name)
        if not month:
            return None
        day = int(m.group('day'))
        year = int(m.group('year'))
        return _validate_and_format(year, month, day)

    # Day with 3-letter month abbreviation
    m = DAY_ABBR_MONTH_RE.match(text)
    if m:
        month_abbr = m.group('month').lower()
        month = MONTH_MAP.get(month_abbr)
        if not month:
            return None
        day = int(m.group('day'))
        year = int(m.group('year'))
        return _validate_and_format(year, month, day)

    # No format matched
    return None

# If run as a script, demonstrate usage with some examples.
if __name__ == "__main__":
    examples = [
        "2024-03-05",
        " 5/3/2024 ",
        "March 5, 2024",
        "5 Mar 2024",
        "31/02/2024",   # invalid
        "Feb 30, 2024"  # invalid
    ]
    for ex in examples:
        print(f"{ex!r} -> {normalize_date(ex)!r}")
