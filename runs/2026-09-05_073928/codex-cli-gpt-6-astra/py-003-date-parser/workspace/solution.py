import re
from datetime import date

_MONTHS = (
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
)
_FULL_MONTHS = {name: number for number, name in enumerate(_MONTHS, 1)}
_SHORT_MONTHS = {name[:3]: number for number, name in enumerate(_MONTHS, 1)}


def normalize_date(text: str) -> str | None:
    text = text.strip()

    if match := re.fullmatch(r"([0-9]{4})-([0-9]{2})-([0-9]{2})", text):
        year, month, day = map(int, match.groups())
    elif match := re.fullmatch(r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})", text):
        day, month, year = map(int, match.groups())
    elif match := re.fullmatch(r"([A-Za-z]+) ([0-9]{1,2}), ([0-9]{4})", text):
        name, day_text, year_text = match.groups()
        month = _FULL_MONTHS.get(name.lower())
        if month is None:
            return None
        day, year = int(day_text), int(year_text)
    elif match := re.fullmatch(r"([0-9]{1,2}) ([A-Za-z]{3}) ([0-9]{4})", text):
        day_text, name, year_text = match.groups()
        month = _SHORT_MONTHS.get(name.lower())
        if month is None:
            return None
        day, year = int(day_text), int(year_text)
    else:
        return None

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
