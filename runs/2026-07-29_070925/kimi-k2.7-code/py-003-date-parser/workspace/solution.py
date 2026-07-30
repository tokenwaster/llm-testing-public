import re
from datetime import date

_MONTH_FULL = {
    name.lower(): i
    for i, name in enumerate(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        start=1,
    )
}

_MONTH_ABBR = {
    name.lower(): i
    for i, name in enumerate(
        [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        start=1,
    )
}

_ISO_RE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
_SLASH_RE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$")
_FULL_RE = re.compile(r"^\s*([A-Za-z]+)\s+(\d{1,2})\s*,\s*(\d{4})\s*$")
_ABBR_RE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\s*$")


def normalize_date(text: str) -> str | None:
    """Convert a date string in one of four supported formats to ISO ``YYYY-MM-DD``."""
    if not isinstance(text, str):
        return None

    def make(year: int, month: int, day: int) -> str | None:
        try:
            date(year, month, day)
        except ValueError:
            return None
        return f"{year:04d}-{month:02d}-{day:02d}"

    m = _ISO_RE.match(text)
    if m:
        return make(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = _SLASH_RE.match(text)
    if m:
        return make(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    m = _FULL_RE.match(text)
    if m:
        month = _MONTH_FULL.get(m.group(1).lower())
        if month is None:
            return None
        return make(int(m.group(3)), month, int(m.group(2)))

    m = _ABBR_RE.match(text)
    if m:
        month = _MONTH_ABBR.get(m.group(2).lower())
        if month is None:
            return None
        return make(int(m.group(3)), month, int(m.group(1)))

    return None
