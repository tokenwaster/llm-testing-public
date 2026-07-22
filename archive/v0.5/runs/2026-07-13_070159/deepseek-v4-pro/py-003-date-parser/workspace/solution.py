import re
import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: YYYY-MM-DD (ISO)
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        try:
            dt = datetime.date.fromisoformat(text)
            return text
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY (slashes, zero-padded or not)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            dt = datetime.date(year, month, day)
            return dt.isoformat()
        except ValueError:
            return None
    
    # Format 3: "Month DD, YYYY" (full month name)
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text)
    if m:
        month_name, day, year = m.group(1), int(m.group(2)), int(m.group(3))
        try:
            month = datetime.datetime.strptime(month_name, '%B').month
            dt = datetime.date(year, month, day)
            return dt.isoformat()
        except ValueError:
            return None
    
    # Format 4: "DD Mon YYYY" (3-letter abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if m:
        day, mon_abbr, year = int(m.group(1)), m.group(2), int(m.group(3))
        try:
            month = datetime.datetime.strptime(mon_abbr, '%b').month
            dt = datetime.date(year, month, day)
            return dt.isoformat()
        except ValueError:
            return None
    
    return None
