from datetime import datetime
import re

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    month_abbr = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    # Format 1: YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        try:
            datetime.strptime(text, '%Y-%m-%d')
            return text
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            date = datetime(year, month, day)
            return date.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 3: "Month D, YYYY"
    match = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$', text)
    if match:
        month_str, day, year = match.group(1).lower(), int(match.group(2)), int(match.group(3))
        if month_str not in month_names:
            return None
        month = month_names[month_str]
        try:
            date = datetime(year, month, day)
            return date.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 4: "D Mon YYYY"
    match = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if match:
        day, month_str, year = int(match.group(1)), match.group(2).lower(), int(match.group(3))
        if month_str not in month_abbr:
            return None
        month = month_abbr[month_str]
        try:
            date = datetime(year, month, day)
            return date.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    return None
