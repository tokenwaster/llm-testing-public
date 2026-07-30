import re
from datetime import date


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: YYYY-MM-DD (ISO, zero-padded)
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY or D/M/YYYY (slashes, zero-padded or not)
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None

    months_full = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
    }

    months_abbr = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    }

    # Format 3: Month DD, YYYY (full month name, comma required)
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$', text)
    if m:
        month_name, day_str, year_str = m.group(1), m.group(2), m.group(3)
        month_num = months_full.get(month_name.lower())
        if month_num is not None:
            try:
                return date(int(year_str), month_num, int(day_str)).isoformat()
            except ValueError:
                return None

    # Format 4: D MMM YYYY (day, 3-letter abbreviation)
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m:
        day_str, month_abbr, year_str = m.group(1), m.group(2), m.group(3)
        month_num = months_abbr.get(month_abbr.lower())
        if month_num is not None:
            try:
                return date(int(year_str), month_num, int(day_str)).isoformat()
            except ValueError:
                return None

    return None
