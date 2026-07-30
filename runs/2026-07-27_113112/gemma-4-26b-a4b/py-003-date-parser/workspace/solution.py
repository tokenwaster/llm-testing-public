from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    Returns None if the format is unrecognized or the date is invalid.
    """
    if not isinstance(text, str):
        return None

    # Remove surrounding whitespace
    t = text.strip()
    if not t:
        return None

    # Define the four accepted formats and whether to use .title() for case-insensitivity.
    # Format 1: YYYY-MM-DD (ISO)
    # Format 2: DD/MM/YYYY (Slashes, zero-padded or not)
    # Format 3: Month Day, Year (Full English month name)
    # Format 4: Day Mon Year (3-letter English abbreviation)
    formats = [
        ("%Y-%m-%d", False),
        ("%d/%m/%Y", False),
        ("%B %d, %Y", True),
        ("%d %b %Y", True)
    ]

    for fmt, use_title in formats:
        try:
            # For month-name based formats (3 and 4), use .title() to ensure 
            # "march" or "MARCH" becomes "March", making parsing case-insensitive.
            parse_text = t.title() if use_title else t
            dt = datetime.strptime(parse_text, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # If the current format doesn't match or the date is invalid (e.g., Feb 31),
            # continue to the next format in the list.
            continue

    return None
