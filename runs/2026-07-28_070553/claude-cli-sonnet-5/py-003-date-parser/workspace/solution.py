import re
from datetime import date

_MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]
_MONTH_ABBR = [m[:3] for m in _MONTHS]


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None

    # Format 1: ISO YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        year, month, day = (int(x) for x in m.groups())
        return _to_iso(year, month, day)

    # Format 2: D/M/Y with slashes, zero-padded or not
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _to_iso(year, month, day)

    # Format 3: "March 5, 2024"
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        month_name, day, year = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        if month_name not in _MONTHS:
            return None
        month = _MONTHS.index(month_name) + 1
        return _to_iso(year, month, day)

    # Format 4: "5 Mar 2024"
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        day, month_abbr, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        if month_abbr not in _MONTH_ABBR:
            return None
        month = _MONTH_ABBR.index(month_abbr) + 1
        return _to_iso(year, month, day)

    return None


def _to_iso(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
