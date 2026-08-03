import re
import datetime

FULL_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

ABBREVS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def normalize_date(text: str) -> str | None:
    s = text.strip()

    # Format 1: YYYY-MM-DD (hyphen-separated, no extra spaces)
    m = re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        year, month, day = map(int, m.groups())
        try:
            datetime.date(year, month, day)
        except ValueError:
            return None
        else:
            return f"{year:04d}-{month:02d}-{day:02d}"

    # Format 2: DD/MM/YYYY (slash-separated, no extra spaces)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        day, month, year = map(int, m.groups())
        try:
            datetime.date(year, month, day)
        except ValueError:
            return None
        else:
            return f"{year:04d}-{month:02d}-{day:02d}"

    # Format 3: Full month name, day, comma, year (e.g., "March 5,2024")
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d+),\s*(\d{4})', s)
    if m:
        mon_str, day_s, year_s = m.groups()
        try:
            month_num = FULL_MONTHS.get(mon_str.lower())
            if month_num is None:
                raise ValueError
            day, year = int(day_s), int(year_s)
            datetime.date(year, month_num, day)
        except ValueError:
            return None
        else:
            return f"{year:04d}-{month_num:02d}-{day:02d}"

    # Format 4: Day, abbreviation (3 letters), year (e.g., "5 Mar 2024")
    m = re.fullmatch(r'(\d+)\s+([A-Za-z]+)\s+(\d{4})', s)
    if m:
        day_s, mon_str, year_s = m.groups()
        try:
            month_num = ABBREVS.get(mon_str.lower())
            if month_num is None:
                raise ValueError
            day, year = int(day_s), int(year_s)
            datetime.date(year, month_num, day)
        except ValueError:
            return None
        else:
            return f"{year:04d}-{month_num:02d}-{day:02d}"

    # No format matched or date is invalid
    return None
