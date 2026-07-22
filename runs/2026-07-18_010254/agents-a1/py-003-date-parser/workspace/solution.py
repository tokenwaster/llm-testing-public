import re
from datetime import date

def normalize_date(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None

    # Format 1: YYYY-MM-DD (ISO) - Strictly two digits for month/day based on example
    m1 = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m1:
        try:
            y, mo, d = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
            date(y, mo, d)  # Validates real calendar date (e.g. Feb 30 raises ValueError)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY - Day/Month/Year with slashes, padding optional
    m2 = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m2:
        try:
            d, mo, y = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
            date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 3: MonthName D, YYYY - Full month name, day, comma, year
    m3 = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$', text)
    if m3:
        month_name = m3.group(1).title()  # Normalize to Title Case (e.g., "march" -> "March")
        day = int(m3.group(2))
        year = int(m3.group(3))
        
        months_full = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        month_num = months_full.get(month_name)
        if month_num is None:
            return None
            
        try:
            date(year, month_num, day)
            return f"{year:04d}-{month_num:02d}-{day:02d}"
        except ValueError:
            return None

    # Format 4: D Mon YYYY - Day, 3-letter abbreviation, year
    m4 = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m4:
        day = int(m4.group(1))
        month_abbr = m4.group(2).title()  # Normalize to Title Case (e.g., "mar" -> "Mar")
        year = int(m4.group(3))
        
        months_short = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        
        month_num = months_short.get(month_abbr)
        if month_num is None:
            return None
            
        try:
            date(year, month_num, day)
            return f"{year:04d}-{month_num:02d}-{day:02d}"
        except ValueError:
            return None

    return None
