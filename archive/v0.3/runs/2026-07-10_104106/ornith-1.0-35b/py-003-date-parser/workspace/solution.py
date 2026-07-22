import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Format 1: YYYY-MM-DD (ISO)
    m = re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)
    if m:
        try:
            dt = datetime.strptime(text, '%Y-%m-%d')
            return f'{dt.year:04d}-{dt.month:02d}-{dt.day:02d}'
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY or D/M/YYYY (slashes)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            datetime.strptime(text, '%d/%m/%Y')
            return f'{year:04d}-{month:02d}-{day:02d}'
        except ValueError:
            return None
    
    # Format 3: Month D, YYYY (full month name)
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2})\s*,\s*(\d{4})', text)
    if m:
        month_str, day, year = m.group(1), int(m.group(2)), int(m.group(3))
        try:
            dt = datetime.strptime(f'{month_str} {day}, {year}', '%B %d, %Y')
            return f'{dt.year:04d}-{dt.month:02d}-{dt.day:02d}'
        except ValueError:
            return None
    
    # Format 4: D Mon YYYY (3-letter abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if m:
        day, month_str, year = int(m.group(1)), m.group(2), int(m.group(3))
        try:
            dt = datetime.strptime(f'{day} {month_str} {year}', '%d %b %Y')
            return f'{dt.year:04d}-{dt.month:02d}-{dt.day:02d}'
        except ValueError:
            return None
    
    return None
