import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: ISO YYYY-MM-DD (e.g., "2024-03-05")
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY with slashes (e.g., "05/03/2024" or "5/3/2024")
    m = re.match(r'^(\d+)/(\d+)/(\d{4})$', text)
    if m:
        day, month_str, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            dt = datetime(year, month_str, day)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: Full English month name, day, comma, year (e.g., "March 5, 2024")
    m = re.match(r'^([A-Za-z]+)\s+(\d+),\s*(\d{4})$', text)
    if m:
        month_name = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        _MONTHS = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
        }
        if month_name in _MONTHS:
            try:
                dt = datetime(year, _MONTHS[month_name], day)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None

    # Format 4: Day, abbreviated month, year (e.g., "5 Mar 2024")
    m = re.match(r'^(\d+)\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m:
        day = int(m.group(1))
        month_abbr = m.group(2).lower()
        year = int(m.group(3))
        _ABBREVS = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        }
        if month_abbr in _ABBREVS:
            try:
                dt = datetime(year, _ABBREVS[month_abbr], day)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None

    return None
