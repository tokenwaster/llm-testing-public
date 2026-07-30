import re
from datetime import date


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: ISO YYYY-MM-DD (already validated by regex, then double-check with date)
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m:
        try:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY with slashes (day/month/year)
    m = re.match(r'^(\d+)/(\d+)/(\d{4})$', text)
    if m:
        try:
            d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # Format 3: MonthName DD, YYYY (full English month name, case-insensitive)
    m = re.match(
        r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d+),\s+(\d{4})$',
        text, re.IGNORECASE,
    )
    if m:
        try:
            mo_name = m.group(1).lower()
            d = int(m.group(2))
            y = int(m.group(3))
            month_map = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12,
            }
            month = month_map[mo_name]
            date(y, month, d)
            return f"{y:04d}-{month:02d}-{d:02d}"
        except (ValueError, KeyError):
            return None

    # Format 4: DD Mon YYYY (day, 3-letter abbreviation, case-insensitive)
    m = re.match(
        r'^(\d+)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})$',
        text, re.IGNORECASE,
    )
    if m:
        try:
            d = int(m.group(1))
            mo_name = m.group(2).lower()
            y = int(m.group(3))
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            }
            month = month_map[mo_name]
            date(y, month, d)
            return f"{y:04d}-{month:02d}-{d:02d}"
        except (ValueError, KeyError):
            return None

    return None
