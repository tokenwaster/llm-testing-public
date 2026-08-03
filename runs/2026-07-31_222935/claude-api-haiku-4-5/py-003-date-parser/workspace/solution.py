import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: ISO YYYY-MM-DD
    iso_pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    match = re.match(iso_pattern, text)
    if match:
        year, month, day = match.groups()
        try:
            datetime(int(year), int(month), int(day))
            return f"{year}-{month}-{day}"
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY (day/month/year with slashes)
    dmy_pattern = r'^(\d{1,2})/(\d{1,2})/(\d{4})$'
    match = re.match(dmy_pattern, text)
    if match:
        day, month, year = match.groups()
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 3: "March 5, 2024" (full month name, day, comma, year)
    full_month_pattern = r'^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$'
    match = re.match(full_month_pattern, text)
    if match:
        month_name, day, year = match.groups()
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        month_num = month_map.get(month_name.lower())
        if month_num is not None:
            try:
                dt = datetime(int(year), month_num, int(day))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    # Format 4: "5 Mar 2024" (day, 3-letter month abbreviation, year)
    abbr_month_pattern = r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$'
    match = re.match(abbr_month_pattern, text)
    if match:
        day, month_abbr, year = match.groups()
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        month_num = month_map.get(month_abbr.lower())
        if month_num is not None:
            try:
                dt = datetime(int(year), month_num, int(day))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    return None
