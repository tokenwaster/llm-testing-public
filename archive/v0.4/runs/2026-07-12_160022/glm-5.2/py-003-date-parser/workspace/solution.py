import re
from datetime import date

_MONTHS_FULL = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

_MONTHS_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

def normalize_date(text: str) -> str | None:
    s = text.strip()
    if not s:
        return None

    # 1. ISO YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None

    # 2. DD/MM/YYYY (slashes, day/month/year)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        d, mo, y = map(int, m.groups())
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None

    # 3. Full month name, day, comma, year
    m = re.fullmatch(r'([A-Za-z]+) (\d{1,2}), (\d{4})', s)
    if m:
        month_str, d_str, y_str = m.groups()
        mo = _MONTHS_FULL.get(month_str.lower())
        if mo is None:
            return None
        d = int(d_str)
        y = int(y_str)
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None

    # 4. Day, 3-letter month abbreviation, year
    m = re.fullmatch(r'(\d{1,2}) ([A-Za-z]{3}) (\d{4})', s)
    if m:
        d_str, month_str, y_str = m.groups()
        mo = _MONTHS_ABBR.get(month_str.lower())
        if mo is None:
            return None
        d = int(d_str)
        y = int(y_str)
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None

    return None
