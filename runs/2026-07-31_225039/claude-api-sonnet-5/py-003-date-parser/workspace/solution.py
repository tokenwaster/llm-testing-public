import re
from datetime import date

_MONTHS_FULL = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]

_MONTHS_ABBR = [m[:3] for m in _MONTHS_FULL]


def normalize_date(text: str) -> "str | None":
    if text is None:
        return None
    s = text.strip()
    if not s:
        return None

    # Format 1: ISO YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            d = date(year, month, day)
        except ValueError:
            return None
        return d.isoformat()

    # Format 2: D/M/Y with slashes
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            d = date(year, month, day)
        except ValueError:
            return None
        return d.isoformat()

    # Format 3: Month D, Y (full month name)
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        month_str, day_str, year_str = m.group(1), m.group(2), m.group(3)
        month_lower = month_str.lower()
        if month_lower in _MONTHS_FULL:
            month = _MONTHS_FULL.index(month_lower) + 1
            day = int(day_str)
            year = int(year_str)
            try:
                d = date(year, month, day)
            except ValueError:
                return None
            return d.isoformat()
        return None

    # Format 4: D Mon Y (3-letter abbreviation)
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        day_str, month_str, year_str = m.group(1), m.group(2), m.group(3)
        month_lower = month_str.lower()
        if month_lower in _MONTHS_ABBR:
            month = _MONTHS_ABBR.index(month_lower) + 1
            day = int(day_str)
            year = int(year_str)
            try:
                d = date(year, month, day)
            except ValueError:
                return None
            return d.isoformat()
        return None

    return None
