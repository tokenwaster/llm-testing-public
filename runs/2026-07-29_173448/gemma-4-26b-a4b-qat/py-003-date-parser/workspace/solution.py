from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    
    Formats supported:
    1. "2024-03-05" (ISO)
    2. "05/03/2024" or "5/3/2024" (D/M/YYYY)
    3. "March 5, 2024" (Full English month, day, comma, year)
    4. "5 Mar 2024" (Day, 3-letter English month abbreviation, year)
    
    Returns:
        str: The date in 'YYYY-MM-DD' format if valid.
        None: If the format is unrecognized or the date is invalid.
    """
    # 1. Strip surrounding whitespace
    text = text.strip()
    if not text:
        return None

    # 2. Handle case-insensitivity for months. 
    # Using .title() converts 'march', 'MAR', or 'mar' to 'March' or 'Mar',
    # which allows datetime.strptime to process them correctly regardless 
    # of the input case.
    text_processed = text.title()

    # 3. Define the patterns to check against
    # %Y-%m-%d: ISO format (2024-03-05)
    # %d/%m/%Y: Day/Month/Year with slashes (05/03/2024, 5/3/2024)
    # %B %d, %Y: Full Month Day, Year (March 5, 2024)
    # %d %b %Y: Day Month(abbr) Year (5 Mar 2024)
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%d %b %Y"
    ]

    for fmt in formats:
        try:
            # Attempt to parse the string using the current format
            dt = datetime.strptime(text_processed, fmt)
            # Return the date formatted as ISO YYYY-MM-DD
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing fails, move to the next format
            continue

    # 4. Return None if no formats matched or if the date is invalid (e.g. 31/02/2024)
    return None
