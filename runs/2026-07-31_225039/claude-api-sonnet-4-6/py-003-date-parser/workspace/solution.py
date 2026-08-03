import re
from datetime import date

MONTH_NAMES = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}

MONTH_ABBREVS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Format 1: YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            d = date(year, month, day)
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY (zero-padded or not)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            d = date(year, month, day)
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 3: Month D, YYYY (full month name)
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text)
    if m:
        month_str = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        month = MONTH_NAMES.get(month_str)
        if month is None:
            return None
        try:
            d = date(year, month, day)
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 4: D Mon YYYY (3-letter abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if m:
        day = int(m.group(1))
        month_str = m.group(2).lower()
        year = int(m.group(3))
        month = MONTH_ABBREVS.get(month_str)
        if month is None:
            return None
        try:
            d = date(year, month, day)
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    return None
