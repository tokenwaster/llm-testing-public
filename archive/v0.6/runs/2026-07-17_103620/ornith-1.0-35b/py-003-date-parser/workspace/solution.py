import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: ISO YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        try:
            dt = datetime.strptime(text, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 2: day/month/year with slashes (zero-padded or not)
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
        try:
            dt = datetime.strptime(text, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: Full English month name, day, comma, year
    if re.match(r'^[A-Za-z]+ \d{1,2}, \d{4}$', text):
        try:
            dt = datetime.strptime(text, '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 4: Day, 3-letter month abbreviation, year
    if re.match(r'^\d{1,2} [A-Za-z]{3} \d{4}$', text):
        try:
            dt = datetime.strptime(text, '%d %b %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    return None
