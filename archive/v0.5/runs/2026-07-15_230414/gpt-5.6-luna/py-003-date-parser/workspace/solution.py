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
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def normalize_date(text: str) -> str | None:
    text = text.strip()

    match = re.fullmatch(r"([0-9]{4})-([0-9]{2})-([0-9]{2})", text)
    if match:
        year, month, day = map(int, match.groups())
    else:
        match = re.fullmatch(r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})", text)
        if match:
            day, month, year = map(int, match.groups())
        else:
            match = re.fullmatch(
                r"([A-Za-z]+) ([0-9]{1,2}), ([0-9]{4})", text
            )
            if match:
                month_name, day, year = match.groups()
                month = _FULL_MONTHS.get(month_name.lower())
                if month is None:
                    return None
                day = int(day)
                year = int(year)
            else:
                match = re.fullmatch(
                    r"([0-9]{1,2}) ([A-Za-z]{3}) ([0-9]{4})", text
                )
                if not match:
                    return None
                day, month_name, year = match.groups()
                month = _ABBREVIATED_MONTHS.get(month_name.lower())
                if month is None:
                    return None
                day = int(day)
                year = int(year)

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
