import re
from datetime import datetime

_MONTH_FULL = {
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

_MONTH_ABBR = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _to_iso(year: int, month: int, day: int) -> str | None:
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # 1. YYYY-MM-DD (ISO)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if m:
        return _to_iso(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # 2. D/M/YYYY or DD/MM/YYYY
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        return _to_iso(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    # 3. Month D, YYYY (full English month name)
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
    if m:
        month = _MONTH_FULL.get(m.group(1).lower())
        if month is None:
            return None
        return _to_iso(int(m.group(3)), month, int(m.group(2)))

    # 4. D Mon YYYY (3-letter English month abbreviation)
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", text)
    if m:
        month = _MONTH_ABBR.get(m.group(2).lower())
        if month is None:
            return None
        return _to_iso(int(m.group(3)), month, int(m.group(1)))

    return None
