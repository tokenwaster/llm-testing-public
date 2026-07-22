from datetime import datetime
import re

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: Already ISO YYYY-MM-DD
    match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if match:
        year, month, day = match.groups()
        try:
            datetime(int(year), int(month), int(day))
            return text
        except ValueError:
            return None
    
    # Format 2: day/month/year with slashes (5/3/2024 or 05/03/2024)
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if match:
        day, month, year = match.groups()
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 3: "March 5, 2024" - full month name, day, comma, year
    match = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$', text)
    if match:
        month_name, day, year = match.groups()
        try:
            dt = datetime.strptime(f'{month_name} {day} {year}', '%B %d %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 4: "5 Mar 2024" - day, 3-letter month abbreviation, year
    match = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if match:
        day, month_abbr, year = match.groups()
        try:
            dt = datetime.strptime(f'{day} {month_abbr} {year}', '%d %b %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    return None
