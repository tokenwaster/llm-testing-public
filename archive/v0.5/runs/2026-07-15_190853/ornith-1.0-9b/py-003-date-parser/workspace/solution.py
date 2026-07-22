import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: YYYY-MM-DD (already ISO, validate and return as-is)
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m:
        try:
            datetime.strptime(text, '%Y-%m-%d')
            return text
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY or D/M/YYYY with slashes (day/month/year)
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            dt = datetime(year, month, day)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: MonthName DD, YYYY (full English month name)
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$', text)
    if m:
        month_name = m.group(1).lower()
        day, year = int(m.group(2)), int(m.group(3))

        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
        }

        if month_name in months:
            try:
                dt = datetime(year, months[month_name], day)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None

    # Format 4: DD MMM YYYY (3-letter English month abbreviation)
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m:
        day, month_abbr, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))

        months_abbrev = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        }

        if month_abbr in months_abbrev:
            try:
                dt = datetime(year, months_abbrev[month_abbr], day)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                return None

    return None
