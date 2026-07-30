import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: Already ISO (YYYY-MM-DD)
    match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            datetime(year, month, day)
            return text
        except ValueError:
            pass
    
    # Format 2: day/month/year (with slashes, zero-padded or not)
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            date_obj = datetime(year, month, day)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Format 3: "March 5, 2024" (full month name, day, comma, 4-digit year)
    match = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$', text)
    if match:
        month_name = match.group(1)
        day = int(match.group(2))
        year = int(match.group(3))
        
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        month = months.get(month_name.lower())
        if month:
            try:
                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                pass
    
    # Format 4: "5 Mar 2024" (day, 3-letter month abbr, 4-digit year)
    match = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if match:
        day = int(match.group(1))
        month_abbr = match.group(2)
        year = int(match.group(3))
        
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        month = months.get(month_abbr.lower())
        if month:
            try:
                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                pass
    
    return None
