import re
import datetime

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None

    # Format 1: YYYY-MM-DD
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', text)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY or D/M/YYYY
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None

    # Format 3: Month D, YYYY
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})$', text)
    if m:
        month_name = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        if month_name in months:
            try:
                return datetime.date(year, months[month_name], day).isoformat()
            except ValueError:
                return None

    # Format 4: D Mon YYYY
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', text)
    if m:
        day = int(m.group(1))
        month_abbr = m.group(2).lower()
        year = int(m.group(3))
        abbrs = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        if month_abbr in abbrs:
            try:
                return datetime.date(year, abbrs[month_abbr], day).isoformat()
            except ValueError:
                return None

    return None
