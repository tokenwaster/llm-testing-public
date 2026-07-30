import re
from datetime import date

_MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]
_ABBR = [m[:3] for m in _MONTHS]

_ISO_RE = re.compile(r'\A(\d{4})-(\d{2})-(\d{2})\Z')
_SLASH_RE = re.compile(r'\A(\d{1,2})/(\d{1,2})/(\d{4})\Z')
_LONG_RE = re.compile(r'\A([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})\Z')
_ABBR_RE = re.compile(r'\A(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\Z')


def _to_iso(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()

    m = _ISO_RE.match(s)
    if m:
        year, month, day = (int(g) for g in m.groups())
        return _to_iso(year, month, day)

    m = _SLASH_RE.match(s)
    if m:
        day, month, year = (int(g) for g in m.groups())
        return _to_iso(year, month, day)

    m = _LONG_RE.match(s)
    if m:
        month_name, day, year = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        if month_name not in _MONTHS:
            return None
        month = _MONTHS.index(month_name) + 1
        return _to_iso(year, month, day)

    m = _ABBR_RE.match(s)
    if m:
        day, month_abbr, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        if month_abbr not in _ABBR:
            return None
        month = _ABBR.index(month_abbr) + 1
        return _to_iso(year, month, day)

    return None
