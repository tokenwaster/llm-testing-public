import datetime
import re

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

ABBR_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def normalize_date(text: str) -> str | None:
    if text is None:
        return None

    s = text.strip()
    if not s:
        return None

    # Format 1: ISO YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            datetime.date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 2: D/M/YYYY or DD/MM/YYYY
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            datetime.date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 3: Month D, YYYY
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        name = m.group(1).lower()
        d = int(m.group(2))
        y = int(m.group(3))
        mo = MONTHS.get(name)
        if mo is None:
            return None
        try:
            datetime.date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 4: D Mon YYYY
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3,4})\s+(\d{4})", s)
    if m:
        d = int(m.group(1))
        abbr = m.group(2).lower()
        y = int(m.group(3))
        mo = ABBR_MONTHS.get(abbr)
        if mo is None:
            return None
        try:
            datetime.date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    return None
