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


def _validate_and_format(year: int, month: int, day: int) -> str | None:
    try:
        dt = datetime.date(year, month, day)
        return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
    except ValueError:
        return None


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    s = text.strip()
    if not s:
        return None

    # 1. ISO format YYYY-MM-DD
    m1 = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m1:
        return _validate_and_format(
            int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        )

    # 2. DD/MM/YYYY or D/M/YYYY
    m2 = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m2:
        return _validate_and_format(
            int(m2.group(3)), int(m2.group(2)), int(m2.group(1))
        )

    # 3. Full month name, day, comma, 4-digit year (e.g. "March 5, 2024")
    m3 = re.match(r"^([a-zA-Z]+)\s+(\d{1,2})\s*,\s*(\d{4})$", s)
    if m3:
        month_name = m3.group(1).lower()
        if month_name in FULL_MONTHS:
            return _validate_and_format(
                int(m3.group(3)), FULL_MONTHS[month_name], int(m3.group(2))
            )

    # 4. Day, 3-letter month abbr, 4-digit year (e.g. "5 Mar 2024")
    m4 = re.match(r"^(\d{1,2})\s+([a-zA-Z]{3})\s+(\d{4})$", s)
    if m4:
        month_abbr = m4.group(2).lower()
        if month_abbr in ABBR_MONTHS:
            return _validate_and_format(
                int(m4.group(3)), ABBR_MONTHS[month_abbr], int(m4.group(1))
            )

    return None
