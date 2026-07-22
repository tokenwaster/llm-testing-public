import datetime
import re


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    s = text.strip()

    _MONTHS_FULL = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    _MONTHS_ABBR = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }

    def _build(year: int, month: int, day: int) -> str | None:
        try:
            d = datetime.date(year, month, day)
        except ValueError:
            return None
        return d.isoformat()

    # Format 1: ISO YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return _build(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # Format 2: D/M/YYYY (day/month/year)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        return _build(int(m.group(3)), int(m.group(2)), int(m.group(1)))

    # Format 3: "March 5, 2024"
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m:
        month = _MONTHS_FULL.get(m.group(1).lower())
        if month is not None:
            return _build(int(m.group(3)), month, int(m.group(2)))
        return None

    # Format 4: "5 Mar 2024"
    m = re.fullmatch(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        month = _MONTHS_ABBR.get(m.group(2).lower())
        if month is not None:
            return _build(int(m.group(3)), month, int(m.group(1)))
        return None

    return None
