import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: YYYY-MM-DD (ISO format)
    match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY (day/month/year with slashes)
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Format 3: Month D, YYYY (e.g., "March 5, 2024")
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    match = re.match(r'^([a-zA-Z]+)\s+(\d{1,2}),\s+(\d{4})$', text)
    if match:
        month_str, day, year = match.group(1), int(match.group(2)), int(match.group(3))
        month = month_names.get(month_str.lower())
        if month:
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # Format 4: D Mon YYYY (e.g., "5 Mar 2024")
    month_abbrevs = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    match = re.match(r'^(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})$', text)
    if match:
        day, month_str, year = int(match.group(1)), match.group(2), int(match.group(3))
        month = month_abbrevs.get(month_str.lower())
        if month:
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    return None
