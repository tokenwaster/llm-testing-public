from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string from one of four specified formats to ISO YYYY-MM-DD.
    Returns None if the input does not match any format or is an invalid calendar date.
    """
    if not isinstance(text, str):
        return None

    # Remove surrounding whitespace as requested
    s = text.strip()

    # The four specified formats:
    # 1. "2024-03-05" -> ISO YYYY-MM-DD
    # 2. "05/03/2024" (or "5/3/2024") -> Day/Month/Year with slashes
    # 3. "March 5, 2024" -> Full English month name, day, comma, year
    # 4. "5 Mar 2024" -> Day, 3-letter English abbreviation, year
    formats = [
        "%Y-%m-%d",   # Format 1
        "%d/%m/%Y",   # Format 2
        "%B %d, %Y",  # Format 3
        "%d %b %Y"    # Format 4
    ]

    for fmt in formats:
        try:
            # Month names/abbreviations are case-insensitive. 
            # .title() converts "MARCH" or "march" to "March", and "MAR" to "Mar".
            # This matches the requirements for %B and %b in standard English locales.
            dt = datetime.strptime(s.title(), fmt)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            # ValueError is raised if strptime cannot parse the string or 
            # if the date is logically invalid (e.g., Feb 31st).
            continue

    return None
