import re
from datetime import date

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    Returns None if the input is invalid or not a real calendar date.
    """
    # Tolerate surrounding whitespace
    text = text.strip()

    # Format 1: "2024-03-05" (ISO)
    m1 = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m1:
        y, m, d = map(int, m1.groups())
        try:
            date(y, m, d)
            return f"{y:04d}-{m:02d}-{d:02d}"
        except ValueError:
            pass

    # Format 2: "05/03/2024" or "5/3/2024" (day/month/year with slashes)
    m2 = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m2:
        d, m, y = map(int, m2.groups())
        try:
            date(y, m, d)
            return f"{y:04d}-{m:02d}-{d:02d}"
        except ValueError:
            pass

    # Format 3: "March 5, 2024" (Full English month name, day, comma, 4-digit year)
    m3 = re.match(r'^([A-Za-z]+) (\d{1,2}), (\d{4})$', text)
    if m3:
        month_str, d_str, y_str = m3.groups()
        y = int(y_str)
        d = int(d_str)
        months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        m = months.get(month_str.lower())
        if m:
            try:
                date(y, m, d)
                return f"{y:04d}-{m:02d}-{d:02d}"
            except ValueError:
                pass

    # Format 4: "5 Mar 2024" (day, 3-letter English month abbreviation, 4-digit year)
    m4 = re.match(r'^(\d{1,2}) ([A-Za-z]{3}) (\d{4})$', text)
    if m4:
        d_str, mon_str, y_str = m4.groups()
        y = int(y_str)
        d = int(d_str)
        abbrs = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4,
            "may": 5, "jun": 6, "jul": 7, "aug": 8,
            "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        m = abbrs.get(mon_str.lower())
        if m:
            try:
                date(y, m, d)
                return f"{y:04d}-{m:02d}-{d:02d}"
            except ValueError:
                pass

    return None
