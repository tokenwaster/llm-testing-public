import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    text = text.strip()
    if not text:
        return None

    # Format 1: ISO YYYY-MM-DD
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        try:
            d = datetime.strptime(text, '%Y-%m-%d')
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY (zero-padded or not)
    if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', text):
        try:
            d = datetime.strptime(text, '%d/%m/%Y')
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: "Month Day, Year" (full English month name)
    if re.fullmatch(r'[A-Za-z]+\s+\d{1,2},\s+\d{4}', text):
        try:
            d = datetime.strptime(text, '%B %d, %Y')
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 4: "Day Mon Year" (3-letter abbreviation)
    if re.fullmatch(r'\d{1,2}\s+[A-Za-z]{3}\s+\d{4}', text):
        try:
            d = datetime.strptime(text, '%d %b %Y')
            return d.strftime('%Y-%m-%d')
        except ValueError:
            return None

    return None
