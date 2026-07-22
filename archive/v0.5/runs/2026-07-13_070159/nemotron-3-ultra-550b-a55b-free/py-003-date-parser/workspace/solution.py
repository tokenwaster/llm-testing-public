import re
import datetime

MONTHS_FULL = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

MONTHS_ABBR = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four supported formats to ISO YYYY-MM-DD.
    Returns None if the string doesn't match a format or isn't a valid calendar date.
    """
    s = text.strip()

    # Format 1: ISO YYYY-MM-DD (already ISO, just validate)
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        try:
            datetime.date.fromisoformat(s)
            return s
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY or D/M/YYYY (slashes, zero-padded or not)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        day, month, year = map(int, m.groups())
        try:
            dt = datetime.date(year, month, day)
            return dt.isoformat()
        except ValueError:
            return None

    # Format 3: MonthName D, YYYY (full English month name, day, comma, year)
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if m:
        month_str, day_str, year_str = m.groups()
        month_lower = month_str.lower()
        if month_lower in MONTHS_FULL:
            month = MONTHS_FULL[month_lower]
            day = int(day_str)
            year = int(year_str)
            try:
                dt = datetime.date(year, month, day)
                return dt.isoformat()
            except ValueError:
                return None
        return None

    # Format 4: D Mon YYYY (day, 3-letter month abbreviation, year)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        day_str, month_str, year_str = m.groups()
        month_lower = month_str.lower()
        if month_lower in MONTHS_ABBR:
            month = MONTHS_ABBR[month_lower]
            day = int(day_str)
            year = int(year_str)
            try:
                dt = datetime.date(year, month, day)
                return dt.isoformat()
            except ValueError:
                return None
        return None

    return None
