import re
from datetime import date

_MONTHS_FULL = {
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

_MONTHS_ABBR = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": None,  # not valid, placeholder to avoid accidental match
    "oct": 10,
    "nov": 11,
    "dec": 12,
}
# Remove placeholder
_MONTHS_ABBR.pop("sept", None)


def _to_iso(y: int, m: int, d: int) -> str | None:
    try:
        date(y, m, d)
    except ValueError:
        return None
    return f"{y:04d}-{m:02d}-{d:02d}"


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None

    # 1. ISO YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = map(int, m.groups())
        return _to_iso(y, mo, d)

    # 2. DD/MM/YYYY (day/month/year)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        d, mo, y = map(int, m.groups())
        return _to_iso(y, mo, d)

    # 3. MonthName D, YYYY (full month name)
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", s)
    if m:
        month_name, day_s, year_s = m.groups()
        mo = _MONTHS_FULL.get(month_name.lower())
        if mo is None:
            return None
        d = int(day_s)
        y = int(year_s)
        return _to_iso(y, mo, d)

    # 4. D Mon YYYY (3-letter abbreviation)
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        day_s, mon_abbr, year_s = m.groups()
        mo = _MONTHS_ABBR.get(mon_abbr.lower())
        if mo is None:
            return None
        d = int(day_s)
        y = int(year_s)
        return _to_iso(y, mo, d)

    return None
