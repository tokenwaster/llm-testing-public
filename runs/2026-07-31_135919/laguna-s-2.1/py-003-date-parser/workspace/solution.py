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


def _build(y: int, mo: int, d: int) -> str | None:
    try:
        return date(y, mo, d).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OverflowError):
        return None


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()

    # 1. ISO: YYYY-MM-DD (strict, zero-padded)
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return _build(int(m[1]), int(m[2]), int(m[3]))

    # 2. day/month/year with slashes (each 1-2 digits)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return _build(int(m[3]), int(m[2]), int(m[1]))

    # 3. Full month name: "March 5, 2024"
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        mo = _MONTHS_FULL.get(m[1].lower())
        if mo is None:
            return None
        return _build(int(m[3]), mo, int(m[2]))

    # 4. Day + 3-letter abbreviation: "5 Mar 2024"
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        mo = _MONTHS_ABBR.get(m[2].lower())
        if mo is None:
            return None
        return _build(int(m[3]), mo, int(m[1]))

    return None
