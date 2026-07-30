import re
from datetime import date


_FULL_MONTHS = {
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

_ABBREVIATED_MONTHS = {
    name[:3]: number for name, number in _FULL_MONTHS.items()
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    text = text.strip()
    year: int
    month: int
    day: int

    if match := re.fullmatch(r"([0-9]{4})-([0-9]{2})-([0-9]{2})", text):
        year, month, day = map(int, match.groups())

    elif match := re.fullmatch(
        r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})", text
    ):
        day, month, year = map(int, match.groups())

    elif match := re.fullmatch(
        r"([A-Za-z]+)\s+([0-9]{1,2}),\s+([0-9]{4})", text
    ):
        month_name, day_text, year_text = match.groups()
        month = _FULL_MONTHS.get(month_name.lower(), 0)
        day = int(day_text)
        year = int(year_text)

    elif match := re.fullmatch(
        r"([0-9]{1,2})\s+([A-Za-z]{3})\s+([0-9]{4})", text
    ):
        day_text, month_name, year_text = match.groups()
        day = int(day_text)
        month = _ABBREVIATED_MONTHS.get(month_name.lower(), 0)
        year = int(year_text)

    else:
        return None

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
