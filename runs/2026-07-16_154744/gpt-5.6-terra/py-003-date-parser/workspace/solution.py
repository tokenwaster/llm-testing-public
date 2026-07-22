import re
from datetime import date


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    text = text.strip()

    month_names = {
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
    month_abbrs = {
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

    year = month = day = None

    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        year, month, day = map(int, match.groups())
    else:
        match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
        if match:
            day, month, year = map(int, match.groups())
        else:
            match = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
            if match:
                month_name, day_text, year_text = match.groups()
                month = month_names.get(month_name.lower())
                if month is None:
                    return None
                day = int(day_text)
                year = int(year_text)
            else:
                match = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", text)
                if match:
                    day_text, month_name, year_text = match.groups()
                    month = month_abbrs.get(month_name.lower())
                    if month is None:
                        return None
                    day = int(day_text)
                    year = int(year_text)
                else:
                    return None

    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
