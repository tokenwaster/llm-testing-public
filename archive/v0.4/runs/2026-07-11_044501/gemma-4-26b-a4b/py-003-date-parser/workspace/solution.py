from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.
    Returns None if the format is unrecognized or the date is invalid.
    """
    if not isinstance(text, str):
        return None
    
    # Remove surrounding whitespace as required
    cleaned = text.strip()
    
    # To handle case-insensitivity for month names and abbreviations (e.g., "march" -> "March"),
    # we use .title(). This works safely with the provided date formats because 
    # numbers and punctuation are unaffected by title casing.
    titled = cleaned.title()
    
    # Define the four allowed formats
    formats = [
        "%Y-%m-%d",   # Format 1: 2024-03-05 (ISO)
        "%d/%m/%Y",   # Format 2: 05/03/2024 or 5/3/2024 (Day/Month/Year with slashes)
        "%B %d, %Y",  # Format 3: March 5, 2024 (Full month name, day, comma, year)
        "%d %b %Y"    # Format 4: 5 Mar 2024 (Day, 3-letter abbreviation, year)
    ]
    
    for fmt in formats:
        try:
            # Attempt to parse the string with the current format
            dt = datetime.strptime(titled, fmt)
            # If successful, return the date in ISO YYYY-MM-DD format
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing fails for this format, try the next one
            continue
            
    # Return None if no formats matched or if the date was invalid (e.g., Feb 31)
    return None
