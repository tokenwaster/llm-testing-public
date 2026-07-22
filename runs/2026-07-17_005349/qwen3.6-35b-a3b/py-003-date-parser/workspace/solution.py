import re
import datetime

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None

    MONTH_MAP = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    patterns = [
        (re.compile(r'^(\d{4})-(\d{1,2})-(\d{1,2})$'), 'iso'),
        (re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{4})$'), 'slash'),
        (re.compile(r'^([A-Za-z]+) (\d{1,2}), (\d{4})$', re.IGNORECASE), 'long'),
        (re.compile(r'^(\d{1,2}) ([A-Za-z]{3}) (\d{4})$', re.IGNORECASE), 'short'),
    ]

    for pattern, fmt in patterns:
        m = pattern.match(text)
        if m:
            try:
                if fmt == 'iso':
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif fmt == 'slash':
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                elif fmt == 'long':
                    mo_str, d, y = m.group(1), int(m.group(2)), int(m.group(3))
                    mo = MONTH_MAP.get(mo_str.lower())
                    if mo is None:
                        return None
                elif fmt == 'short':
                    d, mo_str, y = int(m.group(1)), m.group(2), int(m.group(3))
                    mo = MONTH_MAP.get(mo_str.lower())
                    if mo is None:
                        return None
                
                return datetime.date(y, mo, d).isoformat()
            except ValueError:
                return None
    return None
