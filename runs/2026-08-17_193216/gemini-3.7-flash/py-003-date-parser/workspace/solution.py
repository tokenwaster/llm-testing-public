import datetime
import re

FULL_MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

ABBR_MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()

    # 1. "YYYY-MM-DD"
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mth, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime.date(y, mth, d).isoformat()
        except ValueError:
            return None

    # 2. "DD/MM/YYYY" (e.g. 05/03/2024 or 5/3/2024)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime.date(y, mth, d).isoformat()
        except ValueError:
            return None

    # 3. "March 5, 2024"
    m = re.fullmatch(r"([a-zA-Z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        mth_name, d, y = m.group(1).lower(), int(m.group(2)), int(m.group(3))
        if mth_name in FULL_MONTHS:
            try:
                return datetime.date(y, FULL_MONTHS[mth_name], d).isoformat()
            except ValueError:
                return None

    # 4. "5 Mar 2024"
    m = re.fullmatch(r"(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})", s)
    if m:
        d, mth_name, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        if mth_name in ABBR_MONTHS:
            try:
                return datetime.date(y, ABBR_MONTHS[mth_name], d).isoformat()
            except ValueError:
                return None

    return None
