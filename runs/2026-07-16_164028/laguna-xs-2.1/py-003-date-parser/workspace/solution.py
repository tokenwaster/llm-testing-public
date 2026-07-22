import re
from datetime import datetime, date

def normalize_date(text: str) -> str | None:
    stripped = text.strip()

    # Case 1: ISO format
    try:
        dt = datetime.strptime(stripped, "%Y-%m-%d")
        return stripped
    except ValueError:
        pass

    # Case 2: day/month/year with slashes
    parts = stripped.split('/')
    if len(parts) == 3:
        if len(parts[2]) == 4:
            try:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
                dt = date(year, month, day)
                return dt.isoformat()
            except (ValueError, TypeError):
                pass

    # Case 3: "March 5, 2024"
    match = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})$', stripped)
    if match:
        month_str = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))
        months_full = ['january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december']
        if month_str in months_full:
            month = months_full.index(month_str) + 1
            try:
                dt = date(year, month, day)
                return dt.isoformat()
            except ValueError:
                pass

    # Case 4: "5 Mar 2024"
    match = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', stripped)
    if match:
        day = int(match.group(1))
        month_abbr = match.group(2).lower()
        year = int(match.group(3))
        months_abbr = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                       'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        if month_abbr in months_abbr:
            month = months_abbr.index(month_abbr) + 1
            try:
                dt = date(year, month, day)
                return dt.isoformat()
            except ValueError:
                pass

    return None
