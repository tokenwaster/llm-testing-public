from datetime import date
from typing import Optional

def normalize_date(text: str) -> Optional[str]:
    """
    Convert a date string in one of four allowed formats to ISO 'YYYY-MM-DD'.
    Return None if the input does not match any format or is not a valid calendar date.
    """
    # Allowed month names and abbreviations (lowercase)
    MONTH_FULL = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    MONTH_ABBR = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ]
    # Build lookup from lowercased name/abbreviation to month number (1-based)
    full_to_num = {name: i+1 for i, name in enumerate(MONTH_FULL)}
    abbr_to_num = {abbr: i+1 for i, abbr in enumerate(MONTH_ABBR)}

    s = text.strip()
    if not s:
        return None

    # 1. ISO format: YYYY-MM-DD (exactly, digits and hyphens)
    if len(s) == 10 and s[4] == '-' and s[7] == '-':
        parts = s.split('-')
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            try:
                d = date(year, month, day)
                return d.isoformat()
            except ValueError:
                return None

    # 2. Slash format: D[D]/M[M]/YYYY (allow leading zeros or not)
    parts = s.split('/')
    if len(parts) == 3:
        if all(p.isdigit() for p in parts):
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            # year must be 4-digit (we trust the parser, but check range)
            if 1 <= month <= 12 and 1 <= day <= 31 and year >= 1:
                try:
                    d = date(year, month, day)
                    return d.isoformat()
                except ValueError:
                    return None

    # 3. "Month day, year"  e.g. March 5, 2024
    # Expect exactly one comma after the day
    if ',' in s:
        # Split on spaces and comma
        # Structure: <MonthName> <day>, <year>
        # Use a simple split: replace ',' with space then split
        tokens = s.replace(',', ' ').split()
        if len(tokens) == 3:
            month_name, day_str, year_str = tokens
            month_name_lower = month_name.lower()
            if month_name_lower in full_to_num:
                day = int(day_str) if day_str.lstrip('-').isdigit() else None
                year = int(year_str) if year_str.lstrip('-').isdigit() else None
                if day is not None and year is not None:
                    month = full_to_num[month_name_lower]
                    try:
                        d = date(year, month, day)
                        return d.isoformat()
                    except ValueError:
                        return None

    # 4. "day Mon year"  e.g. 5 Mar 2024
    tokens = s.split()
    if len(tokens) == 3:
        day_str, mon_str, year_str = tokens
        mon_lower = mon_str.lower()
        if mon_lower in abbr_to_num:
            day = int(day_str) if day_str.lstrip('-').isdigit() else None
            year = int(year_str) if year_str.lstrip('-').isdigit() else None
            if day is not None and year is not None:
                month = abbr_to_num[mon_lower]
                try:
                    d = date(year, month, day)
                    return d.isoformat()
                except ValueError:
                    return None

    # No matching format or invalid date
    return None
