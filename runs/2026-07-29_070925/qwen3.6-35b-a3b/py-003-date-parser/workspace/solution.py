import re
from datetime import date

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()
    if not s:
        return None

    # 1. ISO: YYYY-MM-DD
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try: return date(y, mo, d).isoformat()
        except ValueError: return None

    # 2. DD/MM/YYYY
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try: return date(y, mo, d).isoformat()
        except ValueError: return None

    # 3. Full month name
    m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})$', s)
    if m:
        month_str, d, y = m.group(1), int(m.group(2)), int(m.group(3))
        MONTHS = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        mo = MONTHS.get(month_str.lower())
        if mo is not None:
            try: return date(y, mo, d).isoformat()
            except ValueError: return None

    # 4. Abbreviated month
    m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s*(\d{4})$', s)
    if m:
        d, month_str, y = int(m.group(1)), m.group(2), int(m.group(3))
        MONTHS_ABBR = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        mo = MONTHS_ABBR.get(month_str.lower())
        if mo is not None:
            try: return date(y, mo, d).isoformat()
            except ValueError: return None

    return None
