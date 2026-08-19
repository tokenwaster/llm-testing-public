from __future__ import annotations

import re
from datetime import date

_FULL_MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)

_MONTH_FULL = {name: idx for idx, name in enumerate(_FULL_MONTHS, start=1)}
_MONTH_ABBR = {name[:3]: idx for idx, name in enumerate(_FULL_MONTHS, start=1)}

_ISO_RE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
_SLASH_RE = re.compile(r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})")
_FULL_MONTH_RE = re.compile(r"([A-Za-z]+)\s+([0-9]{1,2}),\s+([0-9]{4})")
_ABBR_MONTH_RE = re.compile(r"([0-9]{1,2})\s+([A-Za-z]{3})\s+([0-9]{4})")


def _iso_date_if_valid(year: int, month: int, day: int) -> str | None:
    try:
        date(year, month, day)
    except ValueError:
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()
    if not s:
        return None

    match = _ISO_RE.fullmatch(s)
    if match is not None:
        return _iso_date_if_valid(int(match[1]), int(match[2]), int(match[3]))

    match = _SLASH_RE.fullmatch(s)
    if match is not None:
        day = int(match[1])
        month = int(match[2])
        year = int(match[3])
        return _iso_date_if_valid(year, month, day)

    match = _FULL_MONTH_RE.fullmatch(s)
    if match is not None:
        month = _MONTH_FULL.get(match[1].lower())
        if month is None:
            return None
        return _iso_date_if_valid(int(match[3]), month, int(match[2]))

    match = _ABBR_MONTH_RE.fullmatch(s)
    if match is not None:
        month = _MONTH_ABBR.get(match[2].lower())
        if month is None:
            return None
        return _iso_date_if_valid(int(match[3]), month, int(match[1]))

    return None
