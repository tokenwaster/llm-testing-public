# solution.py

import re
from datetime import date

MONTH_MAP = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12
}

MONTH_ABBR_MAP = {k[:3]: v for k, v in MONTH_MAP.items()}


def _parse_iso(match: re.Match) -> str | None:
    y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
    try:
        date(y, m, d)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except ValueError:
        return None


def _parse_slash(match: re.Match) -> str | None:
    d, m, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
    try:
        date(y, m, d)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except ValueError:
        return None


def _parse_full_month(match: re.Match) -> str | None:
    month_name = match.group(1).lower()
    d = int(match.group(2))
    y = int(match.group(3))
    m = MONTH_MAP.get(month_name)
    if not m:
        return None
    try:
        date(y, m, d)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except ValueError:
        return None


def _parse_abbr_month(match: re.Match) -> str | None:
    month_abbr = match.group(1).lower()
    d = int(match.group(2))
    y = int(match.group(3))
    m = MONTH_ABBR_MAP.get(month_abbr)
    if not m:
        return None
    try:
        date(y, m, d)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except ValueError:
        return None


# Compile regexes with optional surrounding whitespace
ISO_RE = re.compile(r'^\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*$')
SLASH_RE = re.compile(r'^\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$')
FULL_MONTH_RE = re.compile(
    r'^\s*([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})\s*$',
    re.IGNORECASE
)
ABBR_MONTH_RE = re.compile(
    r'^\s*(\w{3})\s+(\d{1,2})\s+(\d{4})\s*$',
    re.IGNORECASE
)


def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of the supported formats to ISO YYYY-MM-DD.
    Return None if the input does not match any format or is not a valid calendar date.
    """
    for pattern, parser in [
        (ISO_RE, _parse_iso),
        (SLASH_RE, _parse_slash),
        (FULL_MONTH_RE, _parse_full_month),
        (ABBR_MONTH_RE, _parse_abbr_month)
    ]:
        match = pattern.match(text)
        if match:
            return parser(match)
    return None
