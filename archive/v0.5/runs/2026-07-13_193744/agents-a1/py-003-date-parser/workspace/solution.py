import re
from datetime import date

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Helper function to validate and format a date
    def try_format(year, month, day):
        try:
            return date(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            return None

    # 1. ISO YYYY-MM-DD (e.g., "2024-03-05")
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if m:
        y, m_val, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        res = try_format(y, m_val, d)
        if res: return res

    # 2. DD/MM/YYYY (e.g., "05/03/2024", "5/3/2024")
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", text)
    if m:
        d, m_val, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        res = try_format(y, m_val, d)
        if res: return res

    # 3. Month Day, Year (Full Name) (e.g., "March 5, 2024")
    months_full = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$", text)
    if m:
        month_str, day_str, year_str = m.groups()
        try:
            y = int(year_str)
            d = int(day_str)
            m_val = months_full.get(month_str.lower())
            if m_val is not None:
                res = try_format(y, m_val, d)
                if res: return res
        except ValueError:
            pass

    # 4. Day Mon Year (Abbreviation) (e.g., "5 Mar 2024")
    months_abbr = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$", text)
    if m:
        day_str, month_str, year_str = m.groups()
        try:
            y = int(year_str)
            d = int(day_str)
            m_val = months_abbr.get(month_str.lower())
            if m_val is not None:
                res = try_format(y, m_val, d)
                if res: return res
        except ValueError:
            pass

    return None
