#!/usr/bin/env python3
"""
Solution for normalizing dates to ISO format.
"""

import re
from datetime import date

# Mapping of month names and abbreviations to numbers
MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

# Regular expressions for the four accepted formats
ISO_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
SLASH_RE = re.compile(
    r"^\s*(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})\s*$"
)
FULL_MONTH_RE = re.compile(
    r"^\s*(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})\s*$"
)
ABBR_MONTH_RE = re.compile(
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
    Convert a date string in one of four formats to ISO YYYY-MM-DD.

    Returns the normalized date or None if invalid.
    """
    # 1. ISO format
    m = ISO_RE.match(text)
    if m:
        y, mo, d = map(int, m.groups())
        return _validate_and_format(y, mo, d)

    # 2. DD/MM/YYYY with slashes
    m = SLASH_RE.match(text)
    if m:
        day = int(m.group("day"))
        month = int(m.group("month"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 3. Full month name: "March 5, 2024"
    m = FULL_MONTH_RE.match(text)
    if m:
        month_name = m.group("month").lower()
        month = MONTH_MAP.get(month_name)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 4. Abbreviated month: "5 Mar 2024"
    m = ABBR_MONTH_RE.match(text)
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


# If run as a script, demonstrate usage with some examples.
if __name__ == "__main__":
    examples = [
        "2024-03-05",
        " 5/3/2024 ",
        "March 5, 2024",
        "5 Mar 2024",
        "31/02/2024",   # invalid
        "13/13/2020"    # invalid month
    ]
    for ex in examples:
        print(f"{ex!r} -> {normalize_date(ex)!r}")
