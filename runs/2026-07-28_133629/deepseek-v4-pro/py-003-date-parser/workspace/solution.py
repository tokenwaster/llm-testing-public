import datetime
import re

def normalize_date(text: str) -> str | None:
    """Convert a date string in one of four formats to ISO YYYY-MM-DD."""
    text = text.strip()
    if not text:
        return None

    FULL_MONTHS = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    ABBR_MONTHS = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ]

    # 1. ISO format: YYYY-MM-DD (strictly zero‑padded)
    match = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if match:
        try:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            dt = datetime.date(year, month, day)
            return dt.isoformat()
        except ValueError:
            return None

    # 2. DD/MM/YYYY (day/month/year with slashes, day/month may lack leading zero)
    match = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if match:
        try:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            dt = datetime.date(year, month, day)
            return dt.isoformat()
        except ValueError:
            return None

    # 3. "Month day, year" (full month name, case‑insensitive)
    match = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', text)
    if match:
        mon_name = match.group(1).lower()
        if mon_name in FULL_MONTHS:
            try:
                month = FULL_MONTHS.index(mon_name) + 1
                day = int(match.group(2))
                year = int(match.group(3))
                dt = datetime.date(year, month, day)
                return dt.isoformat()
            except ValueError:
                return None

    # 4. "day Mon year" (3‑letter abbreviation, case‑insensitive)
    match = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if match:
        mon_abbr = match.group(2).lower()
        if mon_abbr in ABBR_MONTHS:
            try:
                month = ABBR_MONTHS.index(mon_abbr) + 1
                day = int(match.group(1))
                year = int(match.group(3))
                dt = datetime.date(year, month, day)
                return dt.isoformat()
            except ValueError:
                return None

    return None
