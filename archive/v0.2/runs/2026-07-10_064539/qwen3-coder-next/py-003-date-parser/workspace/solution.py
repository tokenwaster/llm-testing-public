from datetime import datetime, date
import re

def normalize_date(text: str) -> str | None:
    if text is None:
        return None
    
    # Strip surrounding whitespace
    text = text.strip()
    
    # Try format 1: ISO format YYYY-MM-DD
    iso_pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    match = re.match(iso_pattern, text)
    if match:
        year, month, day = map(int, match.groups())
        try:
            # Validate it's a real date
            d = date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Try format 2: DD/MM/YYYY or D/M/YYYY (day/month/year with slashes)
    slash_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(slash_pattern, text)
    if match:
        day_str, month_str, year_str = match.groups()
        try:
            day, month, year = int(day_str), int(month_str), int(year_str)
            d = date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Try format 3: "Month DD, YYYY" or "Month D, YYYY"
    # Full English month names
    full_months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    full_month_pattern = r'^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$'
    match = re.match(full_month_pattern, text)
    if match:
        month_name, day_str, year_str = match.groups()
        month_lower = month_name.lower()
        if month_lower in full_months:
            try:
                day, year = int(day_str), int(year_str)
                month = full_months[month_lower]
                d = date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # Try format 4: "DD Mon YYYY" or "D Mon YYYY"
    # 3-letter English month abbreviations
    abbr_months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    abbr_month_pattern = r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$'
    match = re.match(abbr_month_pattern, text)
    if match:
        day_str, month_abbr, year_str = match.groups()
        month_lower = month_abbr.lower()
        if month_lower in abbr_months:
            try:
                day, year = int(day_str), int(year_str)
                month = abbr_months[month_lower]
                d = date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # If none of the patterns matched
    return None
