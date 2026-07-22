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
    
    # Try format 2: DD/MM/YYYY or D/M/YYYY etc with slashes
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
    
    # Try format 3: "March 5, 2024" - full month name
    full_month_pattern = r'^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$'
    match = re.match(full_month_pattern, text)
    if match:
        month_str, day_str, year_str = match.groups()
        try:
            # Convert month name to number (case-insensitive)
            month_lower = month_str.lower()
            months = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            if month_lower not in months:
                return None
            month = months[month_lower]
            day = int(day_str)
            year = int(year_str)
            d = date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, KeyError):
            return None
    
    # Try format 4: "5 Mar 2024" - day, 3-letter month abbreviation
    abbr_month_pattern = r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$'
    match = re.match(abbr_month_pattern, text)
    if match:
        day_str, month_str, year_str = match.groups()
        try:
            # Convert month abbreviation to number (case-insensitive)
            month_lower = month_str.lower()
            months_abbr = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            if month_lower not in months_abbr:
                return None
            month = months_abbr[month_lower]
            day = int(day_str)
            year = int(year_str)
            d = date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, KeyError):
            return None
    
    # If none of the patterns matched
    return None
