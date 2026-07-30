import re
from datetime import date

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Case 1: ISO format (YYYY-MM-DD)
    iso_match = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if iso_match:
        year, month, day = map(int, iso_match.groups())
        try:
            d = date(year, month, day)
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Case 2: D/M/YYYY with slashes
    slash_match = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if slash_match:
        day_str, month_str, year_str = slash_match.groups()
        try:
            day = int(day_str)
            month = int(month_str)
            year = int(year_str)
            d = date(year, month, day)
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            return None
    
    # Case 3: Full month name (e.g., "March 5, 2024")
    full_month_match = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', text)
    if full_month_match:
        month_name, day_str, year_str = full_month_match.groups()
        month_name_lower = month_name.lower()
        months_full = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        try:
            month_num = months_full.index(month_name_lower) + 1
            day = int(day_str)
            year = int(year_str)
            d = date(year, month_num, day)
            return f"{year}-{month_num:02d}-{day:02d}"
        except (ValueError, IndexError):
            return None
    
    # Case 4: Day, three-letter abbreviation (e.g., "5 Mar 2024")
    abbrev_month_match = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if abbrev_month_match:
        day_str, month_abbrev, year_str = abbrev_month_match.groups()
        month_abbrev_lower = month_abbrev.lower()
        months_abbrv = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                        'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        try:
            month_num = months_abbrv.index(month_abbrev_lower) + 1
            day = int(day_str)
            year = int(year_str)
            d = date(year, month_num, day)
            return f"{year}-{month_num:02d}-{day:02d}"
        except (ValueError, IndexError):
            return None
    
    # No match found
    return None
