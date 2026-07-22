from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.
    Supported formats:
    1. YYYY-MM-DD (ISO)
    2. D/M/YYYY or DD/MM/YYYY
    3. Month Day, Year (e.g., March 5, 2024)
    4. D Mon YYYY (e.g., 5 Mar 2024)

    Returns None if the date is invalid or does not match any format.
    """
    if not isinstance(text, str):
        return None

    # Remove surrounding whitespace
    clean_text = text.strip()
    
    # Use title() to handle case-insensitivity for month names and abbreviations.
    # This converts "march", "MARCH", or "mar" into "March" or "Mar".
    title_text = clean_text.title()

    # List of supported date formats for strptime
    formats = [
        "%Y-%m-%d",   # 2024-03-05
        "%d/%m/%Y",   # 05/03/2024 or 5/3/2024
        "%B %d, %Y",  # March 5, 2024
        "%d %b %Y"    # 5 Mar 2024
    ]

    for fmt in formats:
        try:
            # Attempt to parse the date using the current format
            dt = datetime.strptime(title_text, fmt)
            # Return the date in ISO YYYY-MM-DD format
            return dt.date().isoformat()
        except ValueError:
            # If parsing fails for this format, try the next one
            continue

    # Return None if no formats matched or the date was invalid (e.g., Feb 31)
    return None
