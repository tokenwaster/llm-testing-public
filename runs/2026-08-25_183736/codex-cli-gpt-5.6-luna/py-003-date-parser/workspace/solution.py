import re
from datetime import date


_MONTHS = {
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

_ABBREVIATIONS = {
    name[:3]: month for name, month in _MONTHS.items()
}


def normalize_date(text: str) -> str | None:
    text = text.strip()

    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        year, month, day = map(int, match.groups())
        return _format_date(year, month, day)

    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if match:
        day, month, year = map(int, match.groups())
        return _format_date(year, month, day)

    match = re.fullmatch(
        r"([A-Za-z]+) (\d{1,2}), (\d{4})",
        text,
    )
    if match:
        month_name, day, year = match.groups()
        month = _MONTHS.get(month_name.lower())
        if month is not None:
            return _format_date(int(year), month, int(day))

    match = re.fullmatch(
        r"(\d{1,2}) ([A-Za-z]{3}) (\d{4})",
        text,
    )
    if match:
        day, abbreviation, year = match.groups()
        month = _ABBREVIATIONS.get(abbreviation.lower())
        if month is not None:
            return _format_date(int(year), month, int(day))

    return None


def _format_date(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
