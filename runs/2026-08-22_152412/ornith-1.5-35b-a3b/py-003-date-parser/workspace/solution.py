from __future__ import annotations

import re
from datetime import datetime


_MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
}

_ABBREVIATIONS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()

    # Format 1: YYYY-MM-DD (already ISO)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
        return dt.strftime('%Y-%m-%d')

    # Format 2: DD/MM/YYYY (slashes)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        try:
            dt = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
        return dt.strftime('%Y-%m-%d')

    # Format 3: "Month name day, year"
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if m:
        month_num = _MONTHS.get(m.group(1).lower())
        if month_num is None:
            return None
        try:
            dt = datetime(int(m.group(3)), month_num, int(m.group(2)))
        except ValueError:
            return None
        return dt.strftime('%Y-%m-%d')

    # Format 4: "D Mon YYYY" (3-letter abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        month_num = _ABBREVIATIONS.get(m.group(2).lower())
        if month_num is None:
            return None
        try:
            dt = datetime(int(m.group(3)), month_num, int(m.group(1)))
        except ValueError:
            return None
        return dt.strftime('%Y-%m-%d')

    return None
