import re
import datetime

MONTH_NAMES = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}
MONTH_ABBRS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None
        
    # Format 1: YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None

    # Format 3: Month D, YYYY
    m = re.fullmatch(r'([A-Za-z]+) (\d{1,2}), (\d{4})', s)
    if m:
        month_str = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        month = MONTH_NAMES.get(month_str)
        if month:
            try:
                return datetime.date(year, month, day).isoformat()
            except ValueError:
                return None

    # Format 4: D Mon YYYY
    m = re.fullmatch(r'(\d{1,2}) ([A-Za-z]{3}) (\d{4})', s)
    if m:
        day = int(m.group(1))
        month_str = m.group(2).lower()
        year = int(m.group(3))
        month = MONTH_ABBRS.get(month_str)
        if month:
            try:
                return datetime.date(year, month, day).isoformat()
            except ValueError:
                return None
                
    return None
