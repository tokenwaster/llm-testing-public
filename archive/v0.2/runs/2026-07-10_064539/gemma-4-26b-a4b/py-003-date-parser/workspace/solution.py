from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.
    Formats supported:
    1. "2024-03-05" (ISO)
    2. "05/03/2024" or "5/3/2024" (day/month/year with slashes)
    3. "March 5, 2024" (full month name, day, comma, year)
    4. "5 Mar 2024" (day, 3-letter abbreviation, year)

    Returns None if the format is unrecognized or the date is invalid.
    """
    if not isinstance(text, str):
        return None

    # Remove surrounding whitespace as required
    t = text.strip()
    
    # Use .title() to handle case-insensitivity for month names/abbreviations.
    # This ensures "march", "MARCH", or "mArCh" all become "March".
    # It also handles abbreviations like "mar" -> "Mar".
    t_titled = t.title()

    # Define the four supported formats as specified in the requirements.
    formats = [
        "%Y-%m-%d",    # Format 1: ISO YYYY-MM-DD
        "%d/%m/%Y",    # Format 2: DD/MM/YYYY (handles zero-padded or not)
        "%B %d, %Y",   # Format 3: Full Month Day, Year
        "%d %b %Y"     # Format 4: Day Abbr Month Year
    ]

    for fmt in formats:
        try:
            # Attempt to parse the date string with the current format.
            # datetime.strptime handles invalid dates (like Feb 31) by raising ValueError.
            dt = datetime.strptime(t_titled, fmt)
            # If successful, return the date in ISO YYYY-MM-DD format.
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing fails for this format, continue to the next one.
            continue

    # Return None if none of the formats matched or the date was invalid.
    return None
