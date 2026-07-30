import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: ISO format YYYY-MM-DD
    iso_pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    match = re.match(iso_pattern, text)
    if match:
        try:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    
    # Format 2: day/month/year with slashes (zero-padded or not)
    slash_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(slash_pattern, text)
    if match:
        try:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    
    # Format 3: Full month name, day, comma, year (e.g., "March 5, 2024")
    full_month_pattern = r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$'
    match = re.match(full_month_pattern, text)
    if match:
        month_name = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))
        
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        if month_name in month_map:
            try:
                datetime(year, month_map[month_name], day)
                return f"{year:04d}-{month_map[month_name]:02d}-{day:02d}"
            except ValueError:
                pass
    
    # Format 4: day, abbreviated month, year (e.g., "5 Mar 2024")
    abbrev_month_pattern = r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$'
    match = re.match(abbrev_month_pattern, text)
    if match:
        day = int(match.group(1))
        month_abbrev = match.group(2).lower()
        year = int(match.group(3))
        
        abbrev_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        if month_abbrev in abbrev_map:
            try:
                datetime(year, abbrev_map[month_abbrev], day)
                return f"{year:04d}-{abbrev_map[month_abbrev]:02d}-{day:02d}"
            except ValueError:
                pass
    
    return None
