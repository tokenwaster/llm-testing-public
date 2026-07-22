import re
from datetime import datetime

full_month_names = [
    'January', 'February', 'March', 'April',
    'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December'
]
full_month_map = {name.lower(): (i + 1) for i, name in enumerate(full_month_names)}

abbrev_month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
abbrev_month_map = {name.lower(): (i + 1) for i, name in enumerate(abbrev_month_names)}

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Case 1: "YYYY-MM-DD"
    try:
        dt = datetime.strptime(text, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Case 2: "day/month/year with slashes"
    try:
        dt = datetime.strptime(text, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Case 3: "Month day, year" (full month name)
    match = re.fullmatch(r"([A-Za-z]+)\s+(\d+)\s*,\s*(\d{4})", text)
    if match:
        month_str, day_str, year_str = match.groups()
        month_lower = month_str.lower()
        if month_lower in full_month_map:
            month_num = full_month_map[month_lower]
            day = int(day_str)
            year = int(year_str)
            try:
                dt = datetime(year, month_num, day)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
    
    # Case 4: "day Month abbreviation year"
    match = re.fullmatch(r"(\d+)\s+([A-Za-z]{3})\s+(\d{4})", text)
    if match:
        day_str, abbrev_str, year_str = match.groups()
        abbrev_lower = abbrev_str.lower()
        if abbrev_lower in abbrev_month_map:
            month_num = abbrev_month_map[abbrev_lower]
            day = int(day_str)
            year = int(year_str)
            try:
                dt = datetime(year, month_num, day)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
    
    # None of the cases matched
    return None
