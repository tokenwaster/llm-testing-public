import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()

    # Format 1: ISO YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Format 2: D/M/YYYY (day/month/year, optionally zero-padded)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        day, month, year = m.groups()
        try:
            return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Format 3: Full English month name, day, comma, year -> "March 5, 2024"
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        month_name, day, year = m.groups()
        try:
            dt = datetime.strptime(f"{month_name.capitalize()} {day} {year}", "%B %d %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Format 4: day, 3-letter month abbreviation, year -> "5 Mar 2024"
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        day, mon_abbr, year = m.groups()
        try:
            dt = datetime.strptime(f"{day} {mon_abbr.capitalize()} {year}", "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    return None
