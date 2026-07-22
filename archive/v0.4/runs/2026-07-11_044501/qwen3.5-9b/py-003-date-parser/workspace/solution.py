import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    if not text:
        return None
    
    # Month name mappings (case-insensitive)
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    month_abbrevs = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    # Try ISO format: YYYY-MM-DD
    iso_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
    match = re.match(iso_pattern, text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    
    # Try slash format: DD/MM/YYYY (as specified: day/month/year)
    slash_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(slash_pattern, text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    
    # Try full month name format: Month DD, YYYY (e.g., "March 5, 2024")
    month_pattern = r'^([a-zA-Z]+)\s+(\d{1,2}),\s*(\d{4})$'
    match = re.match(month_pattern, text)
    if match:
        month_name_str, day_str, year_str = match.groups()
        month_name_lower = month_name_str.lower()
        month = month_names.get(month_name_lower)
        if month:
            day = int(day_str)
            year = int(year_str)
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                pass
    
    # Try abbreviated month format: DD MMM YYYY (e.g., "5 Mar 2024")
    abbrev_pattern = r'^(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})$'
    match = re.match(abbrev_pattern, text)
    if match:
        day_str, month_name_str, year_str = match.groups()
        month_name_lower = month_name_str.lower()
        month = month_abbrevs.get(month_name_lower)
        if month:
            day = int(day_str)
            year = int(year_str)
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                pass
    
    return None
