import re
from datetime import date

def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four supported formats to ISO 8601 (YYYY-MM-DD).
    Returns None if the input does not match any format or represents an invalid date.
    """
    s = text.strip()

    # Format 1: ISO 8601 (YYYY-MM-DD)
    try:
        d = date.fromisoformat(s)
        return d.isoformat()
    except ValueError:
        pass

    # Format 2: DD/MM/YYYY or D/M/YYYY (day/month/year with slashes)
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if m:
        day, month, year = map(int, m.groups())
        try:
            d = date(year, month, day)
            return d.isoformat()
        except ValueError:
            return None

    # Format 3: Full month name, day, comma, year (e.g., "March 5, 2024")
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$', s)
    if m:
        month_str, day_str, year_str = m.groups()
        month_lower = month_str.lower()
        if month_lower in month_names:
            month = month_names[month_lower]
            day = int(day_str)
            year = int(year_str)
            try:
                d = date(year, month, day)
                return d.isoformat()
            except ValueError:
                return None

    # Format 4: Day, 3-letter month abbreviation, year (e.g., "5 Mar 2024")
    month_abbrevs = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', s)
    if m:
        day_str, month_str, year_str = m.groups()
        month_lower = month_str.lower()
        if month_lower in month_abbrevs:
            month = month_abbrevs[month_lower]
            day = int(day_str)
            year = int(year_str)
            try:
                d = date(year, month, day)
                return d.isoformat()
            except ValueError:
                return None

    # No matching format or invalid date
    return None
