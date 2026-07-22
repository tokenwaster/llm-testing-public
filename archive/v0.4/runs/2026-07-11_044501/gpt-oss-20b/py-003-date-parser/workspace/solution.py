#!/usr/bin/env python3
"""
Solution for normalizing dates in various formats to ISO YYYY-MM-DD.
"""

import re
from datetime import date

# Mapping of full month names and abbreviations (case-insensitive) to month numbers
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

# Regular expressions for the four supported formats
ISO_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
DMY_SLASH_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})\s*$"
)
MONTH_DAY_YEAR_RE = re.compile(
    r"""^\s*
        (?P<month_name>[A-Za-z]+)\s+
        (?P<day>\d{1,2}),\s*
        (?P<year>\d{4})
        \s*$
     """, re.VERBOSE
)
DAY_MONTH_ABBR_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})\s+(?P<month_abbr>[A-Za-z]{3})\s+(?P<year>\d{4})\s*$"
)

def _validate_and_format(year: int, month: int, day: int) -> str | None:
    """Validate the date and return ISO string if valid."""
    try:
        d = date(year, month, day)
        return d.isoformat()
    except ValueError:
        return None

def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four supported formats to ISO YYYY-MM-DD.
    Return None if the input does not match any format or is not a valid calendar date.
    """
    # 1. ISO format
    m = ISO_RE.match(text)
    if m:
        y, mo, d = map(int, m.groups())
        return _validate_and_format(y, mo, d)

    # 2. DD/MM/YYYY with slashes
    m = DMY_SLASH_RE.match(text)
    if m:
        day = int(m.group("day"))
        month = int(m.group("month"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 3. Full month name, day, comma, year
    m = MONTH_DAY_YEAR_RE.match(text)
    if m:
        month_name = m.group("month_name").lower()
        month = MONTH_MAP.get(month_name)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 4. Day, 3-letter month abbreviation, year
    m = DAY_MONTH_ABBR_RE.match(text)
    if m:
        month_abbr = m.group("month_abbr").lower()
        month = MONTH_MAP.get(month_abbr)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # No format matched
    return None

# If run as a script, demonstrate usage with some examples
if __name__ == "__main__":
    examples = [
        "2024-03-05",
        " 5/3/2024 ",
        "March 5, 2024",
        "5 Mar 2024",
        "31/02/2024",   # invalid
        "Feb 30, 2020"  # invalid
    ]
    for ex in examples:
        print(f"{ex!r} -> {normalize_date(ex)!r}")
