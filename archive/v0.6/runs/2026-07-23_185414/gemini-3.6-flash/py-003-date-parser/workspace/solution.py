import datetime
import re

FULL_MONTHS = {
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

SHORT_MONTHS = {
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

    text = text.strip()
    if not text:
        return None

    # Format 1: YYYY-MM-DD
    m1 = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if m1:
        year, month, day = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        try:
            return datetime.date(year, month, day).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY (zero-padded or not)
    m2 = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", text)
    if m2:
        day, month, year = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        try:
            return datetime.date(year, month, day).isoformat()
        except ValueError:
            return None

    # Format 3: March 5, 2024 (full English month name, day, comma, 4-digit year)
    m3 = re.match(r"^([a-zA-Z]+)\s+(\d{1,2}),\s*(\d{4})$", text)
    if m3:
        month_str = m3.group(1).lower()
        if month_str in FULL_MONTHS:
            month = FULL_MONTHS[month_str]
            day, year = int(m3.group(2)), int(m3.group(3))
            try:
                return datetime.date(year, month, day).isoformat()
            except ValueError:
                return None

    # Format 4: 5 Mar 2024 (day, 3-letter English month abbreviation, 4-digit year)
    m4 = re.match(r"^(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})$", text)
    if m4:
        day = int(m4.group(1))
        month_str = m4.group(2).lower()
        if month_str in SHORT_MONTHS:
            month = SHORT_MONTHS[month_str]
            year = int(m4.group(3))
            try:
                return datetime.date(year, month, day).isoformat()
            except ValueError:
                return None

    return None
