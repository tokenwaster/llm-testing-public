import datetime
import re

_MONTH_NAMES = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
}

_MONTH_ABBRS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None

    # Format 1: ISO YYYY-MM-DD
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        try:
            d = datetime.date.fromisoformat(s)
            return d.isoformat()
        except ValueError:
            return None

    # Format 2: d/m/Y
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            d = datetime.date(year, month, day)
            return d.isoformat()
        except ValueError:
            return None

    # Format 3: Month D, Y (full English month name)
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', s)
    if m:
        month_name = m.group(1).lower()
        day = int(m.group(2))
        year = int(m.group(3))
        month_num = _MONTH_NAMES.get(month_name)
        if month_num is None:
            return None
        try:
            d = datetime.date(year, month_num, day)
            return d.isoformat()
        except ValueError:
            return None

    # Format 4: D Mon Y (3-letter abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        day = int(m.group(1))
        month_abbr = m.group(2).lower()
        year = int(m.group(3))
        month_num = _MONTH_ABBRS.get(month_abbr)
        if month_num is None:
            return None
        try:
            d = datetime.date(year, month_num, day)
            return d.isoformat()
        except ValueError:
            return None

    return None
