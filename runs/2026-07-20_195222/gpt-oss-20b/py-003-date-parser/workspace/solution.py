#!/usr/bin/env python3
"""
normalize_date module

Provides a single function `normalize_date` that accepts a date string in one of four
formats and returns the ISO 8601 representation (YYYY-MM-DD) or None if invalid.
"""

import re
from datetime import date


# Precompiled regex patterns for each format
ISO_PATTERN = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
DMY_SLASH_PATTERN = re.compile(
    r"^\s*(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})\s*$"
)
MONTH_NAME_PATTERN = re.compile(
    r"""^\s*
        (?P<month_name>[A-Za-z]+)\s+
        (?P<day>\d{1,2}),?\s+
        (?P<year>\d{4})
        \s*$
    """,
    re.VERBOSE,
)
DAY_ABBR_PATTERN = re.compile(
    r"^\s*(?P<day>\d{1,2})\s+(?P<month_abbr>[A-Za-z]{3})\s+(?P<year>\d{4})\s*$"
)

# Mapping of month names and abbreviations to month numbers
MONTH_MAP = {
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
# Abbreviations (first three letters, case-insensitive)
ABBR_MAP = {name[:3].lower(): num for name, num in MONTH_MAP.items()}


def _validate_and_format(year: int, month: int, day: int) -> str | None:
    """Validate the date components and return ISO string if valid."""
    try:
        d = date(year, month, day)
        return d.isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four supported formats to ISO YYYY-MM-DD.

    Supported input formats (whitespace tolerant):
      1. "2024-03-05"          (ISO)
      2. "05/03/2024" or "5/3/2024"
      3. "March 5, 2024"
      4. "5 Mar 2024"

    Returns:
        ISO formatted date string if input is valid, otherwise None.
    """
    # 1. ISO format
    m = ISO_PATTERN.match(text)
    if m:
        year, month, day = map(int, m.groups())
        return _validate_and_format(year, month, day)

    # 2. Day/Month/Year with slashes
    m = DMY_SLASH_PATTERN.match(text)
    if m:
        day = int(m.group("day"))
        month = int(m.group("month"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 3. Full month name
    m = MONTH_NAME_PATTERN.match(text)
    if m:
        month_name = m.group("month_name").lower()
        month = MONTH_MAP.get(month_name)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # 4. Day + 3-letter abbreviation
    m = DAY_ABBR_PATTERN.match(text)
    if m:
        month_abbr = m.group("month_abbr").lower()
        month = ABBR_MAP.get(month_abbr)
        if not month:
            return None
        day = int(m.group("day"))
        year = int(m.group("year"))
        return _validate_and_format(year, month, day)

    # No pattern matched
    return None


# If run as a script, provide simple CLI testing
if __name__ == "__main__":
    import sys

    for line in sys.stdin:
        line = line.rstrip("\n")
        result = normalize_date(line)
        print(result if result is not None else "None")
