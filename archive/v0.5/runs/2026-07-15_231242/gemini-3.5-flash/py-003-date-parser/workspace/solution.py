import re
from datetime import datetime

# Month name mappings
MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

MONTH_ABBRS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

# Regular expressions for the four formats
# 1. YYYY-MM-DD
RE_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

# 2. DD/MM/YYYY (or D/M/YYYY)
RE_SLASH = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")

# 3. Month DD, YYYY (e.g., March 5, 2024)
RE_MONTH_NAME = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$")

# 4. DD Mon YYYY (e.g., 5 Mar 2024)
RE_MONTH_ABBR = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$")

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    s = text.strip()
    
    # Try Format 1: YYYY-MM-DD
    m1 = RE_ISO.match(s)
    if m1:
        year, month, day = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        try:
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Try Format 2: DD/MM/YYYY
    m2 = RE_SLASH.match(s)
    if m2:
        day, month, year = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        try:
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Try Format 3: Month DD, YYYY
    m3 = RE_MONTH_NAME.match(s)
    if m3:
        month_str, day_str, year_str = m3.group(1).lower(), m3.group(2), m3.group(3)
        if month_str in MONTH_NAMES:
            month = MONTH_NAMES[month_str]
            day, year = int(day_str), int(year_str)
            try:
                dt = datetime(year, month, day)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None
        return None

    # Try Format 4: DD Mon YYYY
    m4 = RE_MONTH_ABBR.match(s)
    if m4:
        day_str, month_str, year_str = m4.group(1), m4.group(2).lower(), m4.group(3)
        if month_str in MONTH_ABBRS:
            month = MONTH_ABBRS[month_str]
            day, year = int(day_str), int(year_str)
            try:
                dt = datetime(year, month, day)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None
        return None

    return None
