import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    """Convert a date string to ISO format (YYYY-MM-DD)."""
    
    # Strip whitespace
    text = text.strip()
    
    if not text:
        return None
    
    # Month name mapping for full names
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    # Month abbreviation mapping
    month_abbrs = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    # Try ISO format first (YYYY-MM-DD)
    iso_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
    match = re.match(iso_pattern, text)
    if match:
        year, month, day = match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return f"{date_obj.year:04d}-{date_obj.month:02d}-{date_obj.day:02d}"
        except ValueError:
            return None
    
    # Try day/month/year with slashes (DD/MM/YYYY or D/M/YYYY)
    slash_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(slash_pattern, text)
    if match:
        day, month, year = match.groups()
        try:
            date_obj = datetime(int(year), int(month), int(day))
            return f"{date_obj.year:04d}-{date_obj.month:02d}-{date_obj.day:02d}"
        except ValueError:
            return None
    
    # Try full month name format (Month DD, YYYY)
    month_pattern = r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$'
    match = re.match(month_pattern, text)
    if match:
        month_name, day, year = match.groups()
        month_lower = month_name.lower()
        if month_lower in month_names:
            try:
                date_obj = datetime(int(year), month_names[month_lower], int(day))
                return f"{date_obj.year:04d}-{date_obj.month:02d}-{date_obj.day:02d}"
            except ValueError:
                return None
    
    # Try abbreviated month format (DD MMM YYYY)
    abbr_pattern = r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$'
    match = re.match(abbr_pattern, text)
    if match:
        day, month_abbr, year = match.groups()
        month_lower = month_abbr.lower()
        if month_lower in month_abbrs:
            try:
                date_obj = datetime(int(year), month_abbrs[month_lower], int(day))
                return f"{date_obj.year:04d}-{date_obj.month:02d}-{date_obj.day:02d}"
            except ValueError:
                return None
    
    # If no format matched or date is invalid
    return None
