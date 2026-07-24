from __future__ import annotations

import datetime
import re

FULL_MONTHS = {
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
    'december': 12,
}

ABBR_MONTHS = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}


def normalize_date(text: str) -> str | None:
    s = text.strip()

    # Format 1: YYYY-MM-DD (zero-padded)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        y, mo, d = m.groups()
        try:
            return datetime.date(int(y), int(mo), int(d)).isoformat()
        except ValueError:
            return None

    # Format 2: D/M/YYYY or DD/MM/YYYY with slashes
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        d, mo, y = m.groups()
        try:
            return datetime.date(int(y), int(mo), int(d)).isoformat()
        except ValueError:
            return None

    # Format 3: Full month name, day, comma, 4-digit year
    m = re.fullmatch(r'([A-Za-z]+) (\d{1,2}), (\d{4})', s)
    if m:
        month_str, d, y = m.groups()
        mo = FULL_MONTHS.get(month_str.lower())
        if mo is None:
            return None
        try:
            return datetime.date(int(y), mo, int(d)).isoformat()
        except ValueError:
            return None

    # Format 4: Day, 3-letter month abbreviation, 4-digit year
    m = re.fullmatch(r'(\d{1,2}) ([A-Za-z]{3}) (\d{4})', s)
    if m:
        d, month_str, y = m.groups()
        mo = ABBR_MONTHS.get(month_str.lower())
        if mo is None:
            return None
        try:
            return datetime.date(int(y), mo, int(d)).isoformat()
        except ValueError:
            return None

    return None
