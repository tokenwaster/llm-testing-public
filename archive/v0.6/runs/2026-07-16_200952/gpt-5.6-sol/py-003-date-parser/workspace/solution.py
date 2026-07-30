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

    match = re.fullmatch(r"([0-9]{4})-([0-9]{2})-([0-9]{2})", text)
    if match:
        year, month, day = map(int, match.groups())
    else:
        match = re.fullmatch(
            r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})", text
        )
        if match:
            day, month, year = map(int, match.groups())
        else:
            match = re.fullmatch(
                r"([A-Za-z]+)\s+([0-9]{1,2}),\s+([0-9]{4})", text
            )
            if match:
                month_name, day_text, year_text = match.groups()
                month = _FULL_MONTHS.get(month_name.lower())
                if month is None:
                    return None
                day = int(day_text)
                year = int(year_text)
            else:
                match = re.fullmatch(
                    r"([0-9]{1,2})\s+([A-Za-z]{3})\s+([0-9]{4})", text
                )
                if not match:
                    return None

                day_text, month_name, year_text = match.groups()
                month = _ABBREVIATED_MONTHS.get(month_name.lower())
                if month is None:
                    return None
                day = int(day_text)
                year = int(year_text)

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
