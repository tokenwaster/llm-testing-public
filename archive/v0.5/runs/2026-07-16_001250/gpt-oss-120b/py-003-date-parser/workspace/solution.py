# solution.py
import re
import datetime
import calendar
from typing import Optional

# Mapping for month names and abbreviations (case‑insensitive)
_MONTH_NAME_TO_NUM = {name.lower(): idx for idx, name in enumerate(calendar.month_name) if name}
_MONTH_ABBR_TO_NUM = {abbr.lower(): idx for idx, abbr in enumerate(calendar.month_abbr) if abbr}


def _valid_date(year: int, month: int, day: int) -> Optional[datetime.date]:
    """Return a date object if the components form a real calendar date, else None."""
    try:
        return datetime.date(year, month, day)
    except ValueError:
        return None


def normalize_date(text: str) -> Optional[str]:
    """
    Convert a date string in one of the supported formats to ISO ``YYYY-MM-DD``.
    Return ``None`` if the input does not match any format or is not a real date.
    """
    s = text.strip()

    # 1. ISO format: YYYY-MM-DD (must be zero‑padded)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        d = _valid_date(*map(int, s.split("-")))
        return d.isoformat() if d else None

    # 2. Day/Month/Year with slashes: D/M/YYYY or DD/MM/YYYY
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = map(int, m.groups())
        d = _valid_date(year, month, day)
        return d.isoformat() if d else None

    # 3. Full month name: "March 5, 2024"
    m = re.fullmatch(r"([A-Za-z]+) (\d{1,2}), (\d{4})", s)
    if m:
        month_name, day, year = m.groups()
        month_num = _MONTH_NAME_TO_NUM.get(month_name.lower())
        if month_num:
            d = _valid_date(int(year), month_num, int(day))
            return d.isoformat() if d else None
        return None

    # 4. Day + 3‑letter month abbreviation: "5 Mar 2024"
    m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]{3}) (\d{4})", s)
    if m:
        day, month_abbr, year = m.groups()
        month_num = _MONTH_ABBR_TO_NUM.get(month_abbr.lower())
        if month_num:
            d = _valid_date(int(year), month_num, int(day))
            return d.isoformat() if d else None
        return None

    # No format matched
    return None
