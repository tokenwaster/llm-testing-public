import datetime

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

_MONTHS_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _make_date(year: int, month: int, day: int) -> "str | None":
    try:
        return datetime.date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> "str | None":
    import re

    if not isinstance(text, str):
        return None

    s = text.strip()
    if not s:
        return None

    # Format 1: ISO YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _make_date(year, month, day)

    # Format 2: D/M/YYYY (day/month/year), zero-padded or not
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _make_date(year, month, day)

    # Format 3: Month D, YYYY  (full English month name)
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        month = _MONTHS.get(m.group(1).lower())
        if month is None:
            return None
        day, year = int(m.group(2)), int(m.group(3))
        return _make_date(year, month, day)

    # Format 4: D Mon YYYY  (3-letter English month abbreviation)
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        month = _MONTHS_ABBR.get(m.group(2).lower())
        if month is None:
            return None
        day, year = int(m.group(1)), int(m.group(3))
        return _make_date(year, month, day)

    return None
