import re
from datetime import date

MONTHS_FULL = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
}

MONTHS_ABBR = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None

    # Format 1: ISO YYYY-MM-DD (strict zero-padding required)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            date(y, mo, d)
        except ValueError:
            return None
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # Format 2: DD/MM/YYYY (zero-padding optional)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            date(y, mo, d)
        except ValueError:
            return None
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # Format 3: "Month DD, YYYY" (full English month name)
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text)
    if m:
        month_name = m.group(1).lower()
        if month_name in MONTHS_FULL:
            mo = MONTHS_FULL[month_name]
            d = int(m.group(2))
            y = int(m.group(3))
            try:
                date(y, mo, d)
            except ValueError:
                return None
            return f"{y:04d}-{mo:02d}-{d:02d}"

    # Format 4: "DD Mon YYYY" (3-letter English month abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text)
    if m:
        d = int(m.group(1))
        month_name = m.group(2).lower()
        y = int(m.group(3))
        if month_name in MONTHS_ABBR:
            mo = MONTHS_ABBR[month_name]
            try:
                date(y, mo, d)
            except ValueError:
                return None
            return f"{y:04d}-{mo:02d}-{d:02d}"

    return None
