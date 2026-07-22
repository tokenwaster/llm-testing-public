# solution.py
import datetime
import re
from typing import Optional

# Mapping of month names and abbreviations to month numbers
_FULL_MONTHS = {
    name.lower(): idx
    for idx, name in enumerate(
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

_ABBR_MONTHS = {
    name.lower(): idx
    for idx, name in enumerate(
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


def _valid_date(year: int, month: int, day: int) -> Optional[str]:
    """Return ISO string if the date is valid, otherwise None."""
    try:
        dt = datetime.date(year, month, day)
        return dt.isoformat()
    except ValueError:
        return None


def normalize_date(text: str) -> Optional[str]:
    """
    Convert a date string in one of the supported formats to ISO ``YYYY-MM-DD``.
    Returns ``None`` if the input does not match any format or is not a real date.
    """
    s = text.strip()

    # 1. ISO format: YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        # datetime.date.fromisoformat validates the date
        try:
            return datetime.date.fromisoformat(s).isoformat()
        except ValueError:
            return None

    # 2. DD/MM/YYYY with slashes
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = map(int, m.groups())
        return _valid_date(year, month, day)

    # 3. "MonthName D, YYYY"
    m = re.fullmatch(r"([A-Za-z]+) (\d{1,2}), (\d{4})", s)
    if m:
        month_name, day_str, year_str = m.groups()
        month = _FULL_MONTHS.get(month_name.lower())
        if month is None:
            return None
        day = int(day_str)
        year = int(year_str)
        return _valid_date(year, month, day)

    # 4. "D Mon YYYY"
    m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]{3}) (\d{4})", s)
    if m:
        day_str, month_abbr, year_str = m.groups()
        month = _ABBR_MONTHS.get(month_abbr.lower())
        if month is None:
            return None
        day = int(day_str)
        year = int(year_str)
        return _valid_date(year, month, day)

    # No format matched
    return None
