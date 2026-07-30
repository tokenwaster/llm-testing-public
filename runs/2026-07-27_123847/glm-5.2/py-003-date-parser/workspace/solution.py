import re
from datetime import date

_FULL_MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
}
_ABBR_MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def normalize_date(text: str) -> str | None:
    s = text.strip()
    if not s:
        return None

    # Format 1: YYYY-MM-DD (strict ISO, zero-padded)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        y, mo, d = (int(g) for g in m.groups())
        try:
            date(y, mo, d)
        except ValueError:
            return None
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # Format 2: D/M/YYYY or DD/MM/YYYY (slashes, day/month/year)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        d, mo, y = (int(g) for g in m.groups())
        try:
            date(y, mo, d)
        except ValueError:
            return None
        return f"{y:04d}-{mo:02d}-{d:02d}"

    # Format 3: FullMonth DD, YYYY
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if m:
        name = m.group(1).lower()
        if name in _FULL_MONTHS:
            mo = _FULL_MONTHS[name]
            d = int(m.group(2))
            y = int(m.group(3))
            try:
                date(y, mo, d)
            except ValueError:
                return None
            return f"{y:04d}-{mo:02d}-{d:02d}"
        return None

    # Format 4: DD Mon YYYY (3-letter abbreviation)
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m:
        d = int(m.group(1))
        abbr = m.group(2).lower()
        if abbr in _ABBR_MONTHS:
            mo = _ABBR_MONTHS[abbr]
            y = int(m.group(3))
            try:
                date(y, mo, d)
            except ValueError:
                return None
            return f"{y:04d}-{mo:02d}-{d:02d}"
        return None

    return None
