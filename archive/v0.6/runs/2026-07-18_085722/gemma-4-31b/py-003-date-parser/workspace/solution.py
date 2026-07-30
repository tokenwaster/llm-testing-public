import re
from datetime import date

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    Returns None if the format is invalid or the date does not exist on the calendar.
    """
    if not text:
        return None

    # Tolerate surrounding whitespace
    text = text.strip()

    # Format 1: "2024-03-05" (ISO YYYY-MM-DD)
    # Must be strictly zero-padded to be ISO compliant as per the prompt's example.
    match1 = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match1:
        try:
            y, m, d = map(int, match1.groups())
            return date(y, m, d).isoformat()
        except ValueError:
            return None

    # Format 2: "05/03/2024" or "5/3/2024" (DD/MM/YYYY)
    match2 = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if match2:
        try:
            d, m, y = map(int, match2.groups())
            return date(y, m, d).isoformat()
        except ValueError:
            return None

    # Format 3: "March 5, 2024" (Full Month Day, Year)
    match3 = re.fullmatch(r"([a-zA-Z]+)\s+(\d{1,2}),\s+(\d{4})", text)
    if match3:
        month_str, day_str, year_str = match3.groups()
        months_full = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        m = months_full.get(month_str.lower())
        if m:
            try:
                return date(int(year_str), m, int(day_str)).isoformat()
            except ValueError:
                return None
        else:
            return None

    # Format 4: "5 Mar 2024" (Day Abbr Month Year)
    match4 = re.fullmatch(r"(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})", text)
    if match4:
        day_str, month_str, year_str = match4.groups()
        months_abb = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4,
            "may": 5, "jun": 6, "jul": 7, "aug": 8,
            "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        m = months_abb.get(month_str.lower())
        if m:
            try:
                return date(int(year_str), m, int(day_str)).isoformat()
            except ValueError:
                return None
        else:
            return None

    return None
