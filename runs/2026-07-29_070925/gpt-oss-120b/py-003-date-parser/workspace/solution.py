import re
from datetime import date
from typing import Optional


_MONTH_FULL = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september': 9,
    'october': 10,
    'november': 11,
    'december': 12,
}

_MONTH_ABBR = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}


def _valid_date(y: int, m: int, d: int) -> bool:
    """Return True if y-m-d forms a real Gregorian calendar date."""
    try:
        date(y, m, d)
        return True
    except ValueError:
        return False


def normalize_date(text: str) -> Optional[str]:
    """
    Convert a date string in one of the supported formats to ISO ``YYYY-MM-DD``.
    Supported input formats (whitespace trimmed):
      1. ``YYYY-MM-DD`` (already ISO)
      2. ``DD/MM/YYYY``   – slash separated, day/month may be 1‑ or 2‑digit
      3. ``Monthname D, YYYY`` – full English month name, case‑insensitive
      4. ``D Mon YYYY``   – day, three‑letter month abbreviation, case‑insensitive

    Returns the ISO representation if parsing succeeds and the date is valid;
    otherwise returns ``None``.
    """
    s = text.strip()

    # 1. ISO format
    m_iso = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m_iso:
        y, mo, d = map(int, m_iso.groups())
        if _valid_date(y, mo, d):
            return f'{y:04d}-{mo:02d}-{d:02d}'
        return None

    # 2. DD/MM/YYYY with slashes
    m_slash = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m_slash:
        d, mo, y = map(int, m_slash.groups())
        if _valid_date(y, mo, d):
            return f'{y:04d}-{mo:02d}-{d:02d}'
        return None

    # 3. Full month name: "March 5, 2024"
    m_full = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if m_full:
        month_name, d_str, y_str = m_full.groups()
        month_key = month_name.lower()
        mo = _MONTH_FULL.get(month_key)
        if mo is None:
            return None
        d = int(d_str)
        y = int(y_str)
        if _valid_date(y, mo, d):
            return f'{y:04d}-{mo:02d}-{d:02d}'
        return None

    # 4. Abbreviated month: "5 Mar 2024"
    m_abbr = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if m_abbr:
        d_str, mon_abbr, y_str = m_abbr.groups()
        mo = _MONTH_ABBR.get(mon_abbr.lower())
        if mo is None:
            return None
        d = int(d_str)
        y = int(y_str)
        if _valid_date(y, mo, d):
            return f'{y:04d}-{mo:02d}-{d:02d}'
        return None

    # No matching format
    return None
