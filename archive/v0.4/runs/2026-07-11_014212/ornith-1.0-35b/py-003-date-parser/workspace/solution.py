import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: ISO YYYY-MM-DD (strict, zero-padded month/day)
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m:
        try:
            datetime.strptime(text, '%Y-%m-%d')
            return text
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY or D/M/YYYY (slashes, zero-padded or not)
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            dt = datetime(year, month, day)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: "March 5, 2024" — full English month name, day, comma, year
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$', text)
    if m:
        month_name, day, year = m.group(1), int(m.group(2)), int(m.group(3))
        try:
            dt = datetime.strptime(f"{month_name} {day}, {year}", '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 4: "5 Mar 2024" — day, 3-letter month abbreviation, year
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m:
        day, month_abbr, year = int(m.group(1)), m.group(2), int(m.group(3))
        try:
            dt = datetime.strptime(f"{day} {month_abbr} {year}", '%d %b %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    return None
