import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None

    # Try ISO format first (YYYY-MM-DD)
    iso_match = re.fullmatch(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if iso_match:
        year, month, day = map(int, iso_match.groups())
        try:
            datetime(year=year, month=month, day=day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None

    # Try DD/MM/YYYY format (with or without leading zeros)
    slash_match = re.fullmatch(r'^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$', text)
    if slash_match:
        day, month, year = map(int, slash_match.groups())
        try:
            datetime(year=year, month=month, day=day)
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None

    # Try full month name format (e.g., "March 5, 2024")
    full_month_match = re.fullmatch(r'^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$', text)
    if full_month_match:
        month_name, day, year = full_month_match.groups()
        try:
            month = datetime.strptime(month_name, '%B').month
            datetime(year=int(year), month=month, day=int(day))
            return f"{int(year):04d}-{month:02d}-{int(day):02d}"
        except ValueError:
            return None

    # Try 3-letter month abbreviation format (e.g., "5 Mar 2024")
    abbr_month_match = re.fullmatch(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if abbr_month_match:
        day, month_abbr, year = abbr_month_match.groups()
        try:
            month = datetime.strptime(month_abbr, '%b').month
            datetime(year=int(year), month=month, day=int(day))
            return f"{int(year):04d}-{month:02d}-{int(day):02d}"
        except ValueError:
            return None

    return None
