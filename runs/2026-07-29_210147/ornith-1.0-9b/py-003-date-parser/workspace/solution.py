import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: ISO YYYY-MM-DD (with dashes)
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', text)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY (with slashes, exactly two)
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m:
        try:
            dt = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: Full English month name, day, comma, year
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$', text)
    if m:
        month_lower = m.group(1).lower()
        months_full = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
        }
        if month_lower in months_full:
            try:
                dt = datetime(int(m.group(3)), months_full[month_lower], int(m.group(2)))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None

    # Format 4: Day, 3-letter month abbreviation, year (no comma)
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m:
        month_lower = m.group(2).lower()
        months_abbrev = {k[:3]: v for k, v in months_full.items()}
        if month_lower in months_abbrev:
            try:
                dt = datetime(int(m.group(3)), months_abbrev[month_lower], int(m.group(1)))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None

    return None
