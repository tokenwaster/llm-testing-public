import datetime
import re

_MONTHS = {
    name.lower(): num
    for num, name in enumerate(
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"],
        start=1,
    )
}
_MONTH_ABBREVS = {name[:3]: num for name, num in _MONTHS.items()}

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_SLASH_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_LONG_RE = re.compile(r"^([A-Za-z]+) (\d{1,2}), (\d{4})$")
_ABBREV_RE = re.compile(r"^(\d{1,2}) ([A-Za-z]{3}) (\d{4})$")


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

    m = _SLASH_RE.match(s)
    if m:
        return _build(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = _LONG_RE.match(s)
    if m:
        month = _MONTHS.get(m.group(1).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(2)))

    m = _ABBREV_RE.match(s)
    if m:
        month = _MONTH_ABBREVS.get(m.group(2).lower())
        if month is None:
            return None
        return _build(int(m.group(3)), month, int(m.group(1)))

    return None
