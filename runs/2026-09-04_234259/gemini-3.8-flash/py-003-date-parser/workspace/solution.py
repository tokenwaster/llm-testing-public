import re
from datetime import date

MONTHS_FULL = {
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

MONTHS_ABBR = {
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
    if not isinstance(text, str):
        return None

    s = text.strip()

    # Format 1: "2024-03-05" (ISO YYYY-MM-DD)
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None

    # Format 2: "05/03/2024" (day/month/year)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None

    # Format 3: "March 5, 2024" (full month, day, comma, 4-digit year)
    m = re.fullmatch(r"([a-zA-Z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        month_name = m.group(1).lower()
        if month_name in MONTHS_FULL:
            month = MONTHS_FULL[month_name]
            day, year = int(m.group(2)), int(m.group(3))
            try:
                return date(year, month, day).isoformat()
            except ValueError:
                return None
        return None

    # Format 4: "5 Mar 2024" (day, 3-letter month abbr, 4-digit year)
    m = re.fullmatch(r"(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})", s)
    if m:
        month_abbr = m.group(2).lower()
        if month_abbr in MONTHS_ABBR:
            month = MONTHS_ABBR[month_abbr]
            day, year = int(m.group(1)), int(m.group(3))
            try:
                return date(year, month, day).isoformat()
            except ValueError:
                return None
        return None

    return None
