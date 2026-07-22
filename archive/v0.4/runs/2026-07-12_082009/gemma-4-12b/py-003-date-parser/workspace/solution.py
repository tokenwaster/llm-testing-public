from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    Formats supported:
    1. YYYY-MM-DD
    2. D/M/YYYY or DD/MM/YYYY (day/month/year with slashes)
    3. Month D, YYYY (full English month name, day, comma, 4-digit year)
    4. D Mon YYYY (day, 3-letter English month abbreviation, 4-digit year)

    Returns None if the input is invalid or not a real calendar date.
    """
    # Remove surrounding whitespace
    text = text.strip()
    if not text:
        return None

    # Define the formats to check.
    # For formats involving month names (3 and 4), we use .title() to ensure
    # case-insensitivity as requested by the prompt.
    formats = [
        ("%Y-%m-%d", text),           # Format 1: YYYY-MM-DD
        ("%d/%m/%Y", text),           # Format 2: D/M/YYYY or DD/MM/YYYY
        ("%B %d, %Y", text.title()),  # Format 3: Month D, YYYY (case-insensitive)
        ("%d %b %Y", text.title())    # Format 4: D Mon YYYY (case-insensitive)
    ]

    for fmt, val in formats:
        try:
            # datetime.strptime validates the date (e.g., rejects Feb 31st).
            dt = datetime.strptime(val, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None
