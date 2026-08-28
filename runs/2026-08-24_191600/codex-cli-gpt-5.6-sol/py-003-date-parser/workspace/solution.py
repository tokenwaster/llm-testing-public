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
    name[:3]: number for name, number in _MONTHS.items()
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    text = text.strip()

    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        year, month, day = map(int, match.groups())
    else:
        match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
        if match:
            day, month, year = map(int, match.groups())
        else:
            match = re.fullmatch(
                r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", text
            )
            if match:
                month_name, day_text, year_text = match.groups()
                month = _MONTHS.get(month_name.lower())
                if month is None:
                    return None
                day, year = int(day_text), int(year_text)
            else:
                match = re.fullmatch(
                    r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", text
                )
                if not match:
                    return None
                day_text, month_name, year_text = match.groups()
                month = _ABBREVIATIONS.get(month_name.lower())
                if month is None:
                    return None
                day, year = int(day_text), int(year_text)

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
