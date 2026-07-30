import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    text = text.strip()

    months_full = {
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
    months_abbr = {
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

    def to_iso(year: int, month: int, day: int) -> str | None:
        try:
            datetime(year, month, day)
        except ValueError:
            return None
        return f"{year:04d}-{month:02d}-{day:02d}"

    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return to_iso(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        return to_iso(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
    if m:
        month = months_full.get(m.group(1).lower())
        if month is None:
            return None
        return to_iso(int(m.group(3)), month, int(m.group(2)))

    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", text)
    if m:
        month = months_abbr.get(m.group(2).lower())
        if month is None:
            return None
        return to_iso(int(m.group(3)), month, int(m.group(1)))

    return None
