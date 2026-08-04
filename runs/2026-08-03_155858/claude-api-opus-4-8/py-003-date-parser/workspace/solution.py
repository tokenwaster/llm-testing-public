import re
from datetime import date

_MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

_MONTH_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _make_iso(year: int, month: int, day: int) -> str | None:
    try:
        d = date(year, month, day)
    except ValueError:
        return None
    return d.isoformat()


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()

    # Format 1: ISO YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return _make_iso(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # Format 2: day/month/year with slashes
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return _make_iso(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    # Format 3: "March 5, 2024"
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        month = _MONTH_NAMES.get(m.group(1).lower())
        if month is None:
            return None
        return _make_iso(int(m.group(3)), month, int(m.group(2)))

    # Format 4: "5 Mar 2024"
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        month = _MONTH_ABBR.get(m.group(2).lower())
        if month is None:
            return None
        return _make_iso(int(m.group(3)), month, int(m.group(1)))

    return None
