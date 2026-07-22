import re
import datetime

MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}
ABBR = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def normalize_date(text: str) -> str | None:
    if text is None:
        return None
    s = text.strip()
    if not s:
        return None

    # Format 1: ISO YYYY-MM-DD (zero-padded)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        y, mo, d = (int(x) for x in m.groups())
        try:
            return datetime.date(y, mo, d).isoformat()
        except ValueError:
            return None

    # Format 2: D/M/YYYY or DD/MM/YYYY with slashes (day/month/year)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        d, mo, y = (int(x) for x in m.groups())
        try:
            return datetime.date(y, mo, d).isoformat()
        except ValueError:
            return None

    # Format 3: Month Name Day, Year
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', s)
    if m:
        name, day, year = m.groups()
        mo = MONTHS.get(name.lower())
        if mo is None:
            return None
        try:
            return datetime.date(int(year), mo, int(day)).isoformat()
        except ValueError:
            return None

    # Format 4: Day Abbrev Year
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        day, abbr, year = m.groups()
        mo = ABBR.get(abbr.lower())
        if mo is None:
            return None
        try:
            return datetime.date(int(year), mo, int(day)).isoformat()
        except ValueError:
            return None

    return None
