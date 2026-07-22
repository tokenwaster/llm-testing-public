import re
from datetime import date

def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Mapping of month names to numbers (case insensitive via lowercasing)
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    # 1. ISO format: YYYY-MM-DD (zero-padded)
    iso_re = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')
    m = iso_re.match(text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            date(y, mo, d)
            return text  # already in correct format
        except ValueError:
            return None

    # 2. Day/Month/Year with slashes: D[D]/M[M]/YYYY
    slash_re = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{4})$')
    m = slash_re.match(text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            date(y, mo, d)
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except ValueError:
            return None

    # 3. Full month name, day, year: "Month D, YYYY"
    full_re = re.compile(r'^([a-zA-Z]+) (\d{1,2}), (\d{4})$')
    m = full_re.match(text)
    if m:
        month_name = m.group(1).lower()
        d, y = int(m.group(2)), int(m.group(3))
        mo = months.get(month_name)
        if mo:
            try:
                date(y, mo, d)
                return f"{y:04d}-{mo:02d}-{d:02d}"
            except ValueError:
                pass
        return None

    # 4. Day, abbreviated month, year: "D Mon YYYY"
    abbr_re = re.compile(r'^(\d{1,2}) ([a-zA-Z]{3}) (\d{4})$')
    m = abbr_re.match(text)
    if m:
        d, month_abbr, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        mo = months.get(month_abbr)
        if mo:
            try:
                date(y, mo, d)
                return f"{y:04d}-{mo:02d}-{d:02d}"
            except ValueError:
                pass
        return None

    return None
