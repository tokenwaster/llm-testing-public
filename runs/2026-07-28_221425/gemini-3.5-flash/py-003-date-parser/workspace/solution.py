import datetime
import re

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Format 1: "2024-03-05" -> YYYY-MM-DD (already ISO)
    m1 = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if m1:
        y_str, m_str, d_str = m1.groups()
        try:
            dt = datetime.date(int(y_str), int(m_str), int(d_str))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None
            
    # Format 2: "05/03/2024" -> day/month/year
    m2 = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", text)
    if m2:
        d_str, m_str, y_str = m2.groups()
        try:
            dt = datetime.date(int(y_str), int(m_str), int(d_str))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None
            
    # Format 3: "March 5, 2024" -> full English month name, day, comma, 4-digit year
    m3 = re.match(r"^([a-zA-Z]+)\s+(\d{1,2}),\s*(\d{4})$", text)
    if m3:
        month_str, d_str, y_str = m3.groups()
        months_full = {
            "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
        }
        month_lower = month_str.lower()
        if month_lower in months_full:
            try:
                dt = datetime.date(int(y_str), months_full[month_lower], int(d_str))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None
                
    # Format 4: "5 Mar 2024" -> day, 3-letter English month abbreviation, 4-digit year
    m4 = re.match(r"^(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})$", text)
    if m4:
        d_str, month_str, y_str = m4.groups()
        months_abbr = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        month_lower = month_str.lower()
        if month_lower in months_abbr:
            try:
                dt = datetime.date(int(y_str), months_abbr[month_lower], int(d_str))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None
                
    return None
