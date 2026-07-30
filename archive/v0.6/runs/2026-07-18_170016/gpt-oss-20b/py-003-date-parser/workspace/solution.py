# solution.py

import re
from datetime import date

MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct':10, 'nov':11, 'dec':12
}

# Full month names mapping to numbers
FULL_MONTH_MAP = {name.lower(): num for name, num in MONTH_MAP.items()}

def _parse_iso(s: str):
    """Parse ISO format YYYY-MM-DD."""
    try:
        y, m, d = map(int, s.split('-'))
        return date(y, m, d)
    except Exception:
        return None

def _parse_slash(s: str):
    """Parse DD/MM/YYYY with slashes."""
    try:
        parts = s.split('/')
        if len(parts) != 3:
            return None
        d, m, y = map(int, parts)
        return date(y, m, d)
    except Exception:
        return None

def _parse_full_month(s: str):
    """Parse 'March 5, 2024'."""
    try:
        # pattern: month day, year
        m = re.match(r'^([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})$', s)
        if not m:
            return None
        month_name, d_str, y_str = m.groups()
        month_num = FULL_MONTH_MAP.get(month_name.lower())
        if month_num is None:
            return None
        d = int(d_str)
        y = int(y_str)
        return date(y, month_num, d)
    except Exception:
        return None

def _parse_abbrev(s: str):
    """Parse '5 Mar 2024'."""
    try:
        m = re.match(r'^(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})$', s)
        if not m:
            return None
        d_str, month_abbr, y_str = m.groups()
        month_num = MONTH_MAP.get(month_abbr.lower())
        if month_num is None:
            return None
        d = int(d_str)
        y = int(y_str)
        return date(y, month_num, d)
    except Exception:
        return None

def normalize_date(text: str):
    """
    Convert a date string in one of the supported formats to ISO YYYY-MM-DD.
    
    Returns the normalized string or None if parsing fails or the date is invalid.
    """
    if not isinstance(text, str):
        return None
    s = text.strip()
    # Try each format in order
    for parser in (_parse_iso, _parse_slash, _parse_full_month, _parse_abbrev):
        dt = parser(s)
        if dt:
            return dt.strftime('%Y-%m-%d')
    return None

# Unit tests (simple examples)
if __name__ == "__main__":
    test_cases = [
        ("2024-03-05", "2024-03-05"),
        (" 5/3/2024 ", "2024-03-05"),
        ("March 5, 2024", "2024-03-05"),
        ("5 Mar 2024", "2024-03-05"),
        ("31/02/2024", None),
        ("Feb 30, 2023", None),
        ("13/13/2020", None),
    ]
    for inp, expected in test_cases:
        out = normalize_date(inp)
        assert out == expected, f"Input: {inp!r} Expected: {expected!r} Got: {out!r}"
    print("All tests passed.")
