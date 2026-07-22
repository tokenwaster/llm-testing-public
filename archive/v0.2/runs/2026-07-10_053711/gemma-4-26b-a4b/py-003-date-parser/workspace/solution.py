from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.
    Formats supported:
    1. "2024-03-05" (ISO)
    2. "05/03/2024" or "5/3/2024" (day/month/year with slashes)
    3. "March 5, 2024" (Full month name, day, comma, year)
    4. "5 Mar 2024" (Day, 3-letter abbreviation, year)

    Returns None if the date is invalid or does not match any of the formats.
    """
    if not isinstance(text, str):
        return None

    # Remove surrounding whitespace
    s = text.strip()
    
    # Use .title() to handle case-insensitivity for month names/abbreviations.
    # This converts "march", "MARCH", or "mArCh" into "March".
    # It also handles abbreviations like "mar" -> "Mar".
    s_titled = s.title()

    # Define the supported formats as per requirements
    formats = [
        "%Y-%m-%d",    # Format 1: ISO (YYYY-MM-DD)
        "%d/%m/%Y",    # Format 2: day/month/year with slashes
        "%B %d, %Y",   # Format 3: Full month name, day, comma, year
        "%d %b %Y"     # Format 4: Day, 3-letter abbreviation, year
    ]

    for fmt in formats:
        try:
            # Attempt to parse the string with the current format.
            # strptime handles zero-padding (e.g., '5' vs '05') automatically for %d and %m.
            dt = datetime.strptime(s_titled, fmt)
            # If successful, return the date in ISO YYYY-MM-DD format.
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing fails (either due to format mismatch or invalid calendar date), 
            # continue to the next format.
            continue

    # Return None if no formats matched or if the date was invalid.
    return None
