import re
from datetime import date


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: YYYY-MM-DD (ISO)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return d.isoformat()
        except ValueError:
            return None

    # Format 2: D/M/YYYY or DD/MM/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        try:
            d = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            return d.isoformat()
        except ValueError:
            return None

    # Format 3: Month Day, Year (full month name)
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text)
    if m:
        month_str = m.group(1).capitalize()
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12,
        }
        month = months.get(month_str)
        if month is None:
            return None
        try:
            d = date(int(m.group(3)), month, int(m.group(2)))
            return d.isoformat()
        except ValueError:
            return None

    # Format 4: Day Mon Year (3-letter abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if m:
        month_str = m.group(2).capitalize()
        months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
            'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
            'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
        }
        month = months.get(month_str)
        if month is None:
            return None
        try:
            d = date(int(m.group(3)), month, int(m.group(2)))
            return d.isoformat()
        except ValueError:
            return None

    return None
