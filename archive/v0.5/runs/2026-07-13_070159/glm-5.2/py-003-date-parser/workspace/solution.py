import re
from datetime import date

def normalize_date(text: str) -> str | None:
    s = text.strip()
    if not s:
        return None

    # Format 1: ISO YYYY-MM-DD (zero-padded)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 2: D/M/YYYY (slashes, zero-padded or not)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        d, mo, y = map(int, m.groups())
        try:
            date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 3: Full month name, day, comma, year
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if m:
        month_name = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        months_full = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        if month_name in months_full:
            mo = months_full[month_name]
            try:
                date(year, mo, day)
                return f"{year:04d}-{mo:02d}-{day:02d}"
            except ValueError:
                return None
        else:
            return None

    # Format 4: Day, 3-letter month abbreviation, year
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        day = int(m.group(1))
        month_abbr = m.group(2).lower()
        year = int(m.group(3))
        months_abbr = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4,
            "may": 5, "jun": 6, "jul": 7, "aug": 8,
            "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        if month_abbr in months_abbr:
            mo = months_abbr[month_abbr]
            try:
                date(year, mo, day)
                return f"{year:04d}-{mo:02d}-{day:02d}"
            except ValueError:
                return None
        else:
            return None

    return None
