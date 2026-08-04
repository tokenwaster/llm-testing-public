import re
from datetime import date

def normalize_date(text: str) -> str | None:
    """
    Convert a date string in one of four formats to ISO YYYY-MM-DD.

    Supported formats:
    1. "2024-03-05"  (ISO, two-digit month and day)
    2. "05/03/2024"  or "5/3/2024"  (day/month/year)
    3. "March 5, 2024"  (full month name, day, comma, year)
    4. "5 Mar 2024"  (day, 3-letter month abbreviation, year)

    Returns None for invalid dates or unrecognised formats.
    """
    # Strip surrounding whitespace
    s = text.strip()

    # Full month names (lowercase) -> month number
    full_months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }
    # 3-letter month abbreviations (lowercase) -> month number
    abbr_months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    # ---------- Pattern 1: ISO (YYYY-MM-DD) ----------
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"  # same as input after stripping
        except ValueError:
            return None

    # ---------- Pattern 2: DD/MM/YYYY ----------
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None

    # ---------- Pattern 3: Full month name, day, comma, year ----------
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2})\s*,\s*(\d{4})', s)
    if m:
        month_name = m.group(1).lower()
        month = full_months.get(month_name)
        if month is None:
            return None
        day = int(m.group(2))
        year = int(m.group(3))
        try:
            date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None

    # ---------- Pattern 4: day, 3-letter month abbreviation, year ----------
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        day = int(m.group(1))
        abbr = m.group(2).lower()
        month = abbr_months.get(abbr)
        if month is None:
            return None
        year = int(m.group(3))
        try:
            date(year, month, day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None

    # No pattern matched
    return None
