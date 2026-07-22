from datetime import datetime, date
import re

def normalize_date(text: str) -> str | None:
    if text is None:
        return None
    
    # Strip surrounding whitespace
    text = text.strip()
    
    # If empty after stripping, return None
    if not text:
        return None
    
    # Try format 1: ISO format YYYY-MM-DD
    iso_pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    match = re.match(iso_pattern, text)
    if match:
        year_str, month_str, day_str = match.groups()
        try:
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            # Validate the date
            d = date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Try format 2: DD/MM/YYYY or D/M/YYYY with slashes
    slash_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(slash_pattern, text)
    if match:
        day_str, month_str, year_str = match.groups()
        try:
            day = int(day_str)
            month = int(month_str)
            year = int(year_str)
            # Validate the date
            d = date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Try format 3: Month Day, Year (e.g., "March 5, 2024")
    # Full month names
    full_months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    # Pattern for full month names: Month Day, Year
    full_month_pattern = r'^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$'
    match = re.match(full_month_pattern, text)
    if match:
        month_name, day_str, year_str = match.groups()
        month_lower = month_name.lower()
        if month_lower in full_months:
            try:
                day = int(day_str)
                year = int(year_str)
                month = full_months[month_lower]
                # Validate the date
                d = date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # Try format 4: Day Mon Year (e.g., "5 Mar 2024")
    # Abbreviated month names
    abbrev_months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    # Pattern for abbreviated months: Day Mon Year (no comma)
    abbrev_pattern = r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$'
    match = re.match(abbrev_pattern, text)
    if match:
        day_str, month_abbrev, year_str = match.groups()
        month_lower = month_abbrev.lower()
        if month_lower in abbrev_months:
            try:
                day = int(day_str)
                year = int(year_str)
                month = abbrev_months[month_lower]
                # Validate the date
                d = date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # If none of the patterns matched, return None
    return None
