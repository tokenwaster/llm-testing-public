import re
from datetime import date

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

_MONTH_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_FULL_MONTH_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")
_ABBR_MONTH_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")


def _to_iso(year: int, month: int, day: int) -> str | None:
    try:
        d = date(year, month, day)
    except ValueError:
        return None
    return d.isoformat()


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()
    if not s:
        return None

    m = _ISO_RE.match(s)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _to_iso(year, month, day)

    m = _SLASH_RE.match(s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _to_iso(year, month, day)

    m = _FULL_MONTH_RE.match(s)
    if m:
        month_name, day, year = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        month = _MONTHS.get(month_name)
        if month is None:
            return None
        return _to_iso(year, month, day)

    m = _ABBR_MONTH_RE.match(s)
    if m:
        day, month_abbr, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        month = _MONTH_ABBR.get(month_abbr)
        if month is None:
            return None
        return _to_iso(year, month, day)

    return None
