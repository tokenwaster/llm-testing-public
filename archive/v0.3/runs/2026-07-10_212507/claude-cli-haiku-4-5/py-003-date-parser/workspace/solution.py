import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: Already ISO YYYY-MM-DD
    iso_pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    match = re.match(iso_pattern, text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Format 2: day/month/year with slashes
    slash_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(slash_pattern, text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Format 3: Full month name, day, comma, 4-digit year
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    full_month_pattern = r'^([a-zA-Z]+)\s+(\d{1,2}),\s*(\d{4})$'
    match = re.match(full_month_pattern, text)
    if match:
        month_str = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))
        if month_str in month_names:
            month = month_names[month_str]
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # Format 4: day, 3-letter month abbreviation, 4-digit year
    month_abbrev = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    abbrev_pattern = r'^(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})$'
    match = re.match(abbrev_pattern, text)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()
        year = int(match.group(3))
        if month_str in month_abbrev:
            month = month_abbrev[month_str]
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    return None
