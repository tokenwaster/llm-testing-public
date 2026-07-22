import datetime
import re

_MONTHS_FULL = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

_MONTHS_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_DMY_SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_MONTH_NAME_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")
_DAY_ABBR_RE = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")


def _build(year: int, month: int, day: int) -> str | None:
    try:
        return datetime.date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    s = text.strip()

    m = _ISO_RE.match(s)
    if m:
        return _build(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = _DMY_SLASH_RE.match(s)
    if m:
        return _build(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = _MONTH_NAME_RE.match(s)
    if m:
        month = _MONTHS_FULL.get(m.group(1).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(2)))

    m = _DAY_ABBR_RE.match(s)
    if m:
        month = _MONTHS_ABBR.get(m.group(2).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(1)))

    return None
