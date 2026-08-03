import re
from datetime import date

# Comprehensive mapping for month names and abbreviations (lowercase)
MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    # Abbreviations (standard)
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}

def normalize_date(text: str) -> str | None:
    s = text.strip()
    
    # Format 1: YYYY-MM-DD (ISO)
    try:
        d = date.strptime(s, "%Y-%m-%d")
        return f"{d.year}-{d.month:02d}-{d.day:02d}"
    except ValueError:
        pass
    
    # Format 2: DD/MM/YYYY or D/M/YYYY (slashes)
    try:
        d = date.strptime(s, "%d/%m/%Y")
        return f"{d.year}-{d.month:02d}-{d.day:02d}"
    except ValueError:
        pass
        
    # Format 3: Month Day, Year (e.g., "March 5, 2024")
    m = re.match(r'^([a-zA-Z]+)\s+(\d+)\s*,\s*(\d{4})$', s)
    if m:
        month_str, day_s, year_s = m.groups()
        try:
            m_num = MONTH_MAP.get(month_str.lower())
            if not m_num: raise ValueError
            
            # date constructor validates real calendar dates (e.g. Feb 30 -> error)
            d = date(year=int(year_s), month=m_num, day=int(day_s))
            return f"{d.year}-{d.month:02d}-{d.day:02d}"
        except Exception:
            pass
    
    # Format 4: Day Mon Year (e.g., "5 Mar 2024")
    m = re.match(r'^(\d+)\s+([a-zA-Z]+)\s+(\d{4})$', s)
    if m:
        day_s, month_str, year_s = m.groups()
        try:
            m_num = MONTH_MAP.get(month_str.lower())
            if not m_num: raise ValueError
            
            d = date(year=int(year_s), month=m_num, day=int(day_s))
            return f"{d.year}-{d.month:02d}-{d.day:02d}"
        except Exception:
            pass

    return None
