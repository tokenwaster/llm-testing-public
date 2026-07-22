import datetime
import re

def normalize_date(text: str) -> str | None:
    s = text.strip()
    
    # Try format 1: "YYYY-MM-DD"
    try:
        date_obj = datetime.datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        pass
    
    # Try format 2: D/M/Y with slashes
    parts = s.split('/')
    if len(parts) == 3:
        try:
            day_str, month_str, year_str = parts
            if not (year_str.isdigit() and len(year_str) == 4):
                raise ValueError()
            day = int(day_str)
            month = int(month_str)
            year = int(year_str)
            date_obj = datetime.datetime(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, OverflowError):
            pass
    
    # Try format 3: "Month Day, Year"
    match = re.fullmatch(r"\s*([A-Za-z]+)\s+(\d+)\s*,\s*(\d{4})\s*", s)
    if match:
        month_str, day_str, year_str = match.groups()
        month_map = {
            'january': 1,
            'february': 2,
            'march': 3,
            'april': 4,
            'may': 5,
            'june': 6,
            'july': 7,
            'august': 8,
            'september': 9,
            'october': 10,
            'november': 11,
            'december': 12
        }
        month_str_lower = month_str.lower()
        if month_str_lower in month_map:
            try:
                month = month_map[month_str_lower]
                day = int(day_str)
                year = int(year_str)
                date_obj = datetime.datetime(year, month, day)
                return f"{year}-{month:02d}-{day:02d}"
            except ValueError:
                pass
    
    # Try format 4: "Day MonthAbbr Year"
    match = re.fullmatch(r"\s*(\d+)\s+([A-Za-z]{3})\s+(\d{4})\s*", s)
    if match:
        day_str, month_abbr, year_str = match.groups()
        month_map = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12
        }
        month_abbr_lower = month_abbr.lower()
        if month_abbr_lower in month_map:
            try:
                month = month_map[month_abbr_lower]
                day = int(day_str)
                year = int(year_str)
                date_obj = datetime.datetime(year, month, day)
                return f"{year}-{month:02d}-{day:02d}"
            except ValueError:
                pass
    
    # None of the formats matched
    return None
