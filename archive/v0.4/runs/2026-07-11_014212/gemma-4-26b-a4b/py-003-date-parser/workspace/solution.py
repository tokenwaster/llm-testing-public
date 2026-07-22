from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.
    Formats supported:
    1. YYYY-MM-DD
    2. D/M/YYYY or DD/MM/YYYY
    3. Full Month Day, Year (e.g., March 5, 2024)
    4. D Mon YYYY (e.g., 5 Mar 2024)
    """
    if not isinstance(text, str):
        return None

    # Strip surrounding whitespace and use .title() to handle case-insensitivity
    # for month names/abbreviations (e.g., "march" -> "March", "MAR" -> "Mar").
    s = text.strip().title()

    # List of supported date formats for strptime
    formats = [
        "%Y-%m-%d",   # 2024-03-05
        "%d/%m/%Y",   # 05/03/20int or 5/3/2024
        "%B %d, %Y",  # March 5, 2024
        "%d %b %Y"    # 5 Mar 2024
    ]

    for fmt in formats:
        try:
            # datetime.strptime validates both the format and the calendar date
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing fails for this format, try the next one
            continue

    return None
