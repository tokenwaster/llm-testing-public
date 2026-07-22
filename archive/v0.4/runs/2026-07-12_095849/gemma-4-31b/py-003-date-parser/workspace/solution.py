from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    Returns None if the input does not match any format or is an invalid calendar date.
    """
    if not text:
        return None
    
    # Remove surrounding whitespace as requested
    cleaned = text.strip()
    
    # Format 1: "2024-03-05" — ISO YYYY-MM-DD
    # We check length and dash positions to ensure strict zero-padding for the ISO format.
    if len(cleaned) == 10 and cleaned[4] == '-' and cleaned[7] == '-':
        try:
            dt = datetime.strptime(cleaned, "%Y-%m-%d")
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Format 2: "05/03/2024" — day/month/year with slashes (zero-padded or not)
    try:
        dt = datetime.strptime(cleaned, "%d/%m/%Y")
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # For formats involving English month names, we normalize to Title Case 
    # to ensure case-insensitivity (e.g., "MARCH" -> "March", "mar" -> "Mar").
    titled_cleaned = cleaned.title()
    
    # Format 3: "March 5, 2024" — full English month name, day, comma, 4-digit year
    try:
        dt = datetime.strptime(titled_cleaned, "%B %d, %Y")
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # Format 4: "5 Mar 2024" — day, 3-letter English month abbreviation, 4-digit year
    try:
        dt = datetime.strptime(titled_cleaned, "%d %b %Y")
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        pass

    # Return None if no formats matched or date was invalid (e.g., Feb 31)
    return None
