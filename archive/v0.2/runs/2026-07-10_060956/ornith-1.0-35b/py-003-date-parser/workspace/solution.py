import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    if not text:
        return None
        
    # Format 1: YYYY-MM-DD (ISO)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
            
    # Format 2: DD/MM/YYYY or D/M/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        try:
            dt = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
            
    # Format 3: Full month name, day, comma, year (e.g., "March 5, 2024")
    full_months = '|'.join([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ])
    m = re.fullmatch(rf'({full_months})\s+(\d{{1,2}}),?\s*(\d{{4}})', text, re.IGNORECASE)
    if m:
        try:
            dt = datetime.strptime(f'{m.group(1)} {int(m.group(2))} {m.group(3)}', '%B %d %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
            
    # Format 4: Day, abbreviated month, year (e.g., "5 Mar 2024")
    abbrev_months = '|'.join([
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ])
    m = re.fullmatch(rf'\d{{1,2}}\s+({abbrev_months})\s+(\d{{4}})', text, re.IGNORECASE)
    if m:
        try:
            dt = datetime.strptime(f'{int(m.group(1))} {m.group(2)} {m.group(3)}', '%d %b %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
            
    return None
