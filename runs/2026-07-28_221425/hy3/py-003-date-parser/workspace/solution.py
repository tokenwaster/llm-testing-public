from __future__ import annotations

import re
import datetime

_MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

_ABBREV = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}


def normalize_date(text: str) -> str | None:
    if text is None:
        return None
    text = text.strip()
    if not text:
        return None

    # Format 1: ISO YYYY-MM-DD (strictly zero-padded, 4-digit year)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime.date(y, mo, d).strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 2: D/M/YYYY or DD/MM/YYYY with slashes (day/month/year)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime.date(y, mo, d).strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: "March 5, 2024" (full month name, day, comma, 4-digit year)
    m = re.fullmatch(r'([A-Za-z]+) (\d{1,2}), (\d{4})', text)
    if m:
        month = m.group(1).lower()
        if month not in _MONTHS:
            return None
        mo = _MONTHS[month]
        d = int(m.group(2))
        y = int(m.group(3))
        try:
            return datetime.date(y, mo, d).strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 4: "5 Mar 2024" (day, 3-letter month abbreviation, 4-digit year)
    m = re.fullmatch(r'(\d{1,2}) ([A-Za-z]{3}) (\d{4})', text)
    if m:
        abbr = m.group(2).lower()
        if abbr not in _ABBREV:
            return None
        mo = _ABBREV[abbr]
        d = int(m.group(1))
        y = int(m.group(3))
        try:
            return datetime.date(y, mo, d).strftime('%Y-%m-%d')
        except ValueError:
            return None

    return None
