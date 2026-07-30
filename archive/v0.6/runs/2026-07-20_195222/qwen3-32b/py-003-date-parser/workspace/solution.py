import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    s = text.strip()
    
    # Case 1: ISO format (YYYY-MM-DD)
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Case 2: D/M/Y with slashes
    parts = s.split('/')
    if len(parts) == 3:
        try:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            dt = datetime(year, month, day)
            return f"{year}-{month:02d}-{day:02d}"
        except (ValueError, TypeError):
            pass
    
    # Case 3: "March 5, 2024"
    case3_pattern = r'^\s*([A-Za-z]+)\s+(\d+)\s*,\s*(\d{4})\s*$'
    match = re.match(case3_pattern, s)
    if match:
        month_str = match.group(1).lower().capitalize()
        day_str = match.group(2)
        year_str = match.group(3)
        try:
            day = int(day_str)
            date_str = f"{month_str} {day:02d}, {year_str}"
            dt = datetime.strptime(date_str, "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    
    # Case 4: "5 Mar 2024"
    case4_pattern = r'^\s*(\d+)\s+([A-Za-z]{3})\s+(\d{4})\s*$'
    match = re.match(case4_pattern, s)
    if match:
        day_str = match.group(1)
        month_abbr = match.group(2).lower().capitalize()
        year_str = match.group(3)
        try:
            day = int(day_str)
            date_str = f"{day:02d} {month_abbr} {year_str}"
            dt = datetime.strptime(date_str, "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    
    # None of the cases matched
    return None
