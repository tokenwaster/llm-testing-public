import re
import datetime

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None

    MONTHS = {
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
    
    FULL_MONTHS = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    # Format 1: YYYY-MM-DD
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            datetime.date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            datetime.date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 3: Month D, YYYY
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2})\s*,?\s*(\d{4})$', text)
    if m:
        month_str, d_str, y_str = m.group(1), m.group(2), m.group(3)
        y = int(y_str)
        d = int(d_str)
        month_num = FULL_MONTHS.get(month_str.lower())
        if month_num is None:
            return None
        try:
            datetime.date(y, month_num, d)
            return f"{y:04d}-{month_num:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 4: D Mon YYYY
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m:
        d_str, month_str, y_str = m.group(1), m.group(2), m.group(3)
        y = int(y_str)
        d = int(d_str)
        month_num = MONTHS.get(month_str.lower())
        if month_num is None:
            return None
        try:
            datetime.date(y, month_num, d)
            return f"{y:04d}-{month_num:02d}-{d:02d}"
        except ValueError:
            return None

    return None
