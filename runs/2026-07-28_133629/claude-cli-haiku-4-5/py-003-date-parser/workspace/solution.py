from datetime import datetime
import re

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Format 1: YYYY-MM-DD (ISO format)
    iso_pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    match = re.match(iso_pattern, text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return text
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY (day/month/year with slashes)
    dmy_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(dmy_pattern, text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
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
    
    # Format 3: "March 5, 2024" - full English month name
    fmt3_pattern = r'^([a-zA-Z]+)\s+(\d{1,2}),\s+(\d{4})$'
    match = re.match(fmt3_pattern, text)
    if match:
        month_name, day, year = match.group(1), int(match.group(2)), int(match.group(3))
        month = month_names.get(month_name.lower())
        if month:
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    # Format 4: "5 Mar 2024" - day, 3-letter month abbreviation, year
    fmt4_pattern = r'^(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})$'
    match = re.match(fmt4_pattern, text)
    if match:
        day, month_name, year = int(match.group(1)), match.group(2), int(match.group(3))
        month = month_abbr.get(month_name.lower())
        if month:
            try:
                datetime(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
    
    return None
