#!/usr/bin/env python3
"""
solution.py

Provides a single function `normalize_date` that accepts a date string in one of four
formats and returns the date as an ISO 8601 string (YYYY-MM-DD) or None if the input
is invalid.
"""

import re
from datetime import date, datetime
from typing import Optional

# Precompile regex patterns for each format
ISO_PATTERN = re.compile(r'^\s*(\d{4})-(\d{2})-(\d{2})\s*$')
DMY_SLASH_PATTERN = re.compile(
    r'^\s*([1-9]|[12]\d|3[01])/(0?[1-9]|1[012])/(\d{4})\s*$',
    re.IGNORECASE
)
MONTH_FULL_PATTERN = re.compile(
    r'^\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+([1-9]|[12]\d|3[01]),\s*(\d{4})\s*$',
    re.IGNORECASE
)
MONTH_ABBR_PATTERN = re.compile(
    r'^\s*([1-9]|[12]\d|3[01])\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s*$',
    re.IGNORECASE
)

# Mapping of month names/abbreviations to numbers
MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def _validate_and_format(year: int, month: int, day: int) -> Optional[str]:
    """
    Validate the date components and return ISO string if valid.
    """
    try:
        d = date(year, month, day)
        return d.isoformat()
    except ValueError:
        return None

def normalize_date(text: str) -> Optional[str]:
    """
    Convert a date string in one of four supported formats to an ISO 8601
    string (YYYY-MM-DD). Return None if the input is invalid or not a real date.
    """
    # 1. ISO format
    m = ISO_PATTERN.match(text)
    if m:
        year, month, day = map(int, m.groups())
        return _validate_and_format(year, month, day)

    # 2. DD/MM/YYYY with slashes
    m = DMY_SLASH_PATTERN.match(text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _validate_and_format(year, month, day)

    # 3. Full month name
    m = MONTH_FULL_PATTERN.match(text)
    if m:
        month_name, day, year = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        month = MONTH_MAP.get(month_name)
        return _validate_and_format(year, month, day)

    # 4. Abbreviated month name
    m = MONTH_ABBR_PATTERN.match(text)
    if m:
        day, month_abbr, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        month = MONTH_MAP.get(month_abbr)
        return _validate_and_format(year, month, day)

    # No pattern matched
    return None

# If run as a script, provide simple tests
if __name__ == "__main__":
    test_cases = [
        ("2024-03-05", "2024-03-05"),
        (" 5/3/2024 ", "2024-03-05"),
        ("March 5, 2024", "2024-03-05"),
        ("5 Mar 2024", "2024-03-05"),
        ("31/02/2024", None),
        ("Feb 29, 2019", None),
    ]
    for inp, expected in test_cases:
        result = normalize_date(inp)
        print(f"{inp!r} -> {result!r} (expected: {expected!r})")
