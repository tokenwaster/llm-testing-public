import re
from datetime import date

MONTH_ABBR = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

MONTH_FULL = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

def _make_date(year: int, month: int, day: int):
    try:
        return date(year, month, day)
    except ValueError:
        return None

def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        d = _make_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return d.isoformat() if d else None

    # Format 2: DD/MM/YYYY (zero-padded or not)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        d = _make_date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        return d.isoformat() if d else None

    # Format 3: Month D, YYYY
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text)
    if m:
        month_num = MONTH_FULL.get(m.group(1).lower())
        if month_num is None:
            return None
        d = _make_date(int(m.group(3)), month_num, int(m.group(2)))
        return d.isoformat() if d else None

    # Format 4: D Mon YYYY
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if m:
        month_num = MONTH_ABBR.get(m.group(2).lower())
        if month_num is None:
            return None
        d = _make_date(int(m.group(3)), month_num, int(m.group(1)))
        return d.isoformat() if d else None

    return None
