from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.
    
    Formats supported:
    1. "2024-03-05" (ISO)
    2. "05/03/2024" or "5/3/2024" (Day/Month/Year with slashes)
    3. "March 5, 2024" (Full English month name, day, comma, 4-digit year)
    4. "5 Mar 2024" (Day, 3-letter English month abbreviation, 4-digit year)
    """
    if not isinstance(text, str):
        return None

    # Remove surrounding whitespace as required
    s = text.strip()

    # The four formats to attempt parsing
    formats = [
        "%Y-%m-%d",    # Format 1: ISO
        "%d/%m/%Y",    # Format 2: Day/Month/Year with slashes
        "%B %d, %Y",   # Format 3: Full month name, day, comma, year
        "%d %b %Y"     # Format 4: Day, abbreviated month, year
    ]

    for fmt in formats:
        # First attempt: try parsing the string as-is.
        # This covers ISO and slash formats which are typically not case-sensitive.
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

        # Second attempt: try parsing the string with title casing.
        # This handles case-insensitivity for month names (e.g., "march" -> "March").
        try:
            dt = datetime.strptime(s.title(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # If no formats match or the date is invalid (e.g., Feb 31), return None.
    return None
