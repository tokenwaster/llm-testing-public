import re
from datetime import date

MONTH_MAP = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12
}

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    s = text.strip()
    if not s:
        return None

    # Format 1: YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None

    # Format 3: Month D, YYYY or Month D YYYY
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', s)
    if m:
        month_str = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        month_num = MONTH_MAP.get(month_str)
        if month_num:
            try:
                return date(year, month_num, day).isoformat()
            except ValueError:
                return None

    # Format 4: D Mon YYYY
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', s)
    if m:
        day = int(m.group(1))
        month_str = m.group(2).lower()
        year = int(m.group(3))
        month_num = MONTH_MAP.get(month_str)
        if month_num:
            try:
                return date(year, month_num, day).isoformat()
            except ValueError:
                return None

    return None
