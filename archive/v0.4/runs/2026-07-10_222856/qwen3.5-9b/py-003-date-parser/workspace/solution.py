from datetime import datetime
import re


def normalize_date(text: str) -> str | None:
    """
    Converts a date string to ISO format (YYYY-MM-DD).
    
    Supports four formats:
    1. YYYY-MM-DD (ISO format)
    2. DD/MM/YYYY or D/M/YYYY (day/month/year with slashes)
    3. Month D, YYYY (full month name, day, comma, year)
    4. D MMM YYYY (day, abbreviated month, year)
    
    Returns None for invalid dates or non-matching formats.
    """
    text = text.strip()
    
    if not text:
        return None
    
    # Try ISO format first (YYYY-MM-DD)
    iso_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
    match = re.match(iso_pattern, text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            date_obj = datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Try day/month/year with slashes (DD/MM/YYYY or D/M/YYYY)
    slash_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(slash_pattern, text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            date_obj = datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Try full month name format (Month D, YYYY)
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    full_month_pattern = r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$'
    match = re.match(full_month_pattern, text)
    if match:
        month_name, day_str, year = match.groups()
        month_name_lower = month_name.lower()
        if month_name_lower in month_names:
            month = month_names[month_name_lower]
            day = int(day_str)
            try:
                date_obj = datetime(int(year), month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # Try abbreviated month format (D MMM YYYY)
    month_abbrevs = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    abbrev_month_pattern = r'^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$'
    match = re.match(abbrev_month_pattern, text)
    if match:
        day_str, month_name, year = match.groups()
        month_name_lower = month_name.lower()
        if month_name_lower in month_abbrevs:
            month = month_abbrevs[month_name_lower]
            day = int(day_str)
            try:
                date_obj = datetime(int(year), month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    return None
