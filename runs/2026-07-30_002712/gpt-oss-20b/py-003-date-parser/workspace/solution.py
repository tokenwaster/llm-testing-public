#!/usr/bin/env python3
"""
Solution module for normalize_date function.
"""

import re
from datetime import datetime
from typing import Optional

# Regular expression patterns for the four supported formats
ISO_PATTERN = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
DMY_SLASH_PATTERN = re.compile(
    r"""^\s*
        (\d{1,2})          # day
        /(\d{1,2})         # month
        /(\d{4})           # year
        \s*$
    """,
    re.VERBOSE,
)
FULL_MONTH_PATTERN = re.compile(
    r"""^\s*
        ([A-Za-z]+)        # full month name
        \s+(\d{1,2}),\s+  # day with comma and space
        (\d{4})           # year
        \s*$
    """,
    re.VERBOSE,
)
ABBR_MONTH_PATTERN = re.compile(
    r"""^\s*
        (\d{1,2})          # day
        \s+([A-Za-z]{3})   # 3‑letter month abbreviation
        \s+(\d{4})         # year
        \s*$
    """,
    re.VERBOSE,
)


def _parse_iso(match: re.Match) -> Optional[str]:
    """Parse ISO format after validating the date."""
    try:
        dt = datetime(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
        )
        return dt.date().isoformat()
    except ValueError:
        return None


def _parse_dmy_slash(match: re.Match) -> Optional[str]:
    """Parse day/month/year with slashes."""
    try:
        dt = datetime(
            int(match.group(3)),  # year
            int(match.group(2)),  # month
            int(match.group(1)),  # day
        )
        return dt.date().isoformat()
    except ValueError:
        return None


def _parse_full_month(match: re.Match) -> Optional[str]:
    """Parse full month name format."""
    try:
        dt = datetime.strptime(
            f"{match.group(2)} {match.group(1)} {match.group(3)}",
            "%d %B %Y",
        )
        return dt.date().isoformat()
    except ValueError:
        return None


def _parse_abbr_month(match: re.Match) -> Optional[str]:
    """Parse abbreviated month format."""
    try:
        dt = datetime.strptime(
            f"{match.group(1)} {match.group(2)} {match.group(3)}",
            "%d %b %Y",
        )
        return dt.date().isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> Optional[str]:
    """
    Convert a date string in one of four supported formats to ISO YYYY-MM-DD.

    Parameters
    ----------
    text : str
        The input date string.

    Returns
    -------
    Optional[str]
        ISO formatted date string or None if parsing fails.
    """
    # Check each pattern in order of specificity
    for pattern, parser in [
        (ISO_PATTERN, _parse_iso),
        (DMY_SLASH_PATTERN, _parse_dmy_slash),
        (FULL_MONTH_PATTERN, _parse_full_month),
        (ABBR_MONTH_PATTERN, _parse_abbr_month),
    ]:
        match = pattern.match(text)
        if match:
            return parser(match)

    # No pattern matched
    return None


# If the module is executed directly, run a small test suite.
if __name__ == "__main__":
    tests = [
        ("2024-03-05", "2024-03-05"),
        (" 5/3/2024 ", "2024-03-05"),
        ("March 5, 2024", "2024-03-05"),
        ("5 Mar 2024", "2024-03-05"),
        ("31/02/2024", None),
        ("not a date", None),
    ]
    for inp, expected in tests:
        result = normalize_date(inp)
        print(f"{inp!r} -> {result!r} | {'PASS' if result == expected else 'FAIL'}")
