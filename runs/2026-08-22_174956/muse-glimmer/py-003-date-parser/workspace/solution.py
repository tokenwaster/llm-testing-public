import re
from datetime import datetime

FULL_MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}

ABBR_MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()

    # 1. YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            datetime(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # 2. DD/MM/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        d, mo, y = map(int, m.groups())
        try:
            datetime(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # 3. Month DD, YYYY
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if m:
        month_name, d_str, y_str = m.groups()
        month_key = month_name.lower()
        if month_key in FULL_MONTHS:
            mo = FULL_MONTHS[month_key]
            d = int(d_str)
            y = int(y_str)
            try:
                datetime(y, mo, d)
                return f"{y:04d}-{mo:02d}-{d:02d}"
            except ValueError:
                return None
        return None

    # 4. D Mon YYYY
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        d_str, mon_abbr, y_str = m.groups()
        mon_key = mon_abbr.lower()
        if mon_key in ABBR_MONTHS:
            mo = ABBR_MONTHS[mon_key]
            d = int(d_str)
            y = int(y_str)
            try:
                datetime(y, mo, d)
                return f"{y:04d}-{mo:02d}-{d:02d}"
            except ValueError:
                return None
        return None

    return None
