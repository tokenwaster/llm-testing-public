import re
from datetime import date

_MONTHS = {
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

_ABBRS = {
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


def normalize_date(text: str) -> str | None:
    s = text.strip()

    # 1. Already ISO: YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            date(y, mo, d)
        except ValueError:
            return None
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # 2. day/month/year with slashes
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        d, mo, y = map(int, m.groups())
        try:
            date(y, mo, d)
        except ValueError:
            return None
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # 3. Full month name, day, comma, 4-digit year
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        name = m.group(1).lower()
        if name in _MONTHS:
            mo = _MONTHS[name]
            d = int(m.group(2))
            y = int(m.group(3))
            try:
                date(y, mo, d)
            except ValueError:
                return None
            return f"{y:04d}-{mo:02d}-{d:02d}"
        return None

    # 4. day, 3-letter month abbreviation, 4-digit year
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        abbr = m.group(2).lower()
        if abbr in _ABBRs:
            mo = _ABBRs[abbr]
            d = int(m.group(1))
            y = int(m.group(3))
            try:
                date(y, mo, d)
            except ValueError:
                return None
            return f"{y:04d}-{mo:02d}-{d:02d}"
        return None

    return None
