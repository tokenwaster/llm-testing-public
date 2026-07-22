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

    # Remove surrounding whitespace as required.
    t = text.strip()
    
    # Use .title() to handle case-insensitivity for months and abbreviations.
    # This converts "march" to "March" and "MAR" to "Mar", which are compatible 
    # with strptime's %B and %b directives, while leaving numbers/symbols unchanged.
    t_title = t.title()

    # Define the four supported formats.
    formats = [
        "%Y-%m-%d",   # Format 1: ISO YYYY-MM-DD
        "%d/%m/%Y",   # Format 2: Day/Month/Year with slashes
        "%B %d, %Y",  # Format 3: Full Month Name Day, Year
        "%d %b %Y"    # Format 4: Day Abbreviated Month Year
    ]

    for fmt in formats:
        try:
            # Attempt to parse the string using the current format.
            # datetime.strptime handles both zero-padded and non-zero-padded numbers for %d and %m.
            dt = datetime.strptime(t_title, fmt)
            # If successful, return the date in ISO YYYY-MM-DD format.
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing fails (either due to format mismatch or invalid calendar date), 
            # continue to the next format.
            continue

    # Return None if no formats matched or the date was invalid.
    return None
