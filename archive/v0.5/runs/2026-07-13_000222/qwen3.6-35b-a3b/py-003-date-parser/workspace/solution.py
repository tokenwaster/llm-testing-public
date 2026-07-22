import re
import datetime

def normalize_date(text: str) -> str | None:
    if not text or not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None
        
    # Format 1: YYYY-MM-DD
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', s)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None
            
    # Format 2: DD/MM/YYYY
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None
            
    # Format 3: Month D, YYYY
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})$', s)
    if m:
        month_str, day_str, year_str = m.group(1), m.group(2), m.group(3)
        try:
            dt = datetime.datetime.strptime(f"{month_str} {day_str}, {year_str}", "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None
            
    # Format 4: D Mon YYYY
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', s)
    if m:
        day_str, month_str, year_str = m.group(1), m.group(2), m.group(3)
        try:
            dt = datetime.datetime.strptime(f"{day_str} {month_str} {year_str}", "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None
            
    return None
