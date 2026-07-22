import re
from datetime import date


_MONTHS = {name.lower(): i for i, name in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], start=1)}
_MONTH_ABBRS = {name[:3].lower(): i for name, i in
                ((n, i) for n, i in _MONTHS.items())}

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_DMY_SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_MONTH_NAME_RE = re.compile(r"^([A-Za-z]+) (\d{1,2}), (\d{4})$")
_DAY_ABBR_RE = re.compile(r"^(\d{1,2}) ([A-Za-z]{3}) (\d{4})$")


def _build(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
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
        month = _MONTHS.get(m.group(1).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(2)))

    m = _DAY_ABBR_RE.match(s)
    if m:
        month = _MONTH_ABBRS.get(m.group(2).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(1)))

    return None
