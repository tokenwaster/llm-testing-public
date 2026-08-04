from datetime import datetime
import re

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: ISO YYYY-MM-DD
    if match := re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text):
        year, month, day = map(int, match.groups())
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Format 2: day/month/year (with slashes)
    if match := re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text):
        day, month, year = map(int, match.groups())
        try:
            datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Month name and abbreviation mappings
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    month_abbr = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    # Format 3: Full month name "March 5, 2024"
    if match := re.match(r'^(\w+)\s+(\d{1,2}),\s+(\d{4})$', text):
        month_str, day_str, year_str = match.groups()
        month = month_names.get(month_str.lower())
        if month:
            day, year = int(day_str), int(year_str)
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # Format 4: day, 3-letter abbreviation, year "5 Mar 2024"
    if match := re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})$', text):
        day_str, month_str, year_str = match.groups()
        month = month_abbr.get(month_str.lower())
        if month:
            day, year = int(day_str), int(year_str)
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    return None
