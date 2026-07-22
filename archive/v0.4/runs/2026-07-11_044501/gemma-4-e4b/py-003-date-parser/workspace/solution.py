import datetime
from typing import Optional

def normalize_date(text: str) -> Optional[str]:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.

    Formats supported (in order of attempt):
    1. YYYY-MM-DD (ISO standard)
    2. D/M/Y (Day/Month/Year with slashes, flexible padding)
    3. Full Month Name (e.g., "March 5, 2024")
    4. Abbreviated Month Name (e.g., "5 Mar 2024")

    Returns None if the format is unrecognized or the date is invalid.
    """
    text = text.strip()
    if not text:
        return None

    # List of potential formats and their corresponding strptime codes.
    # We must try them in a specific order, as some formats might overlap 
    # (e.g., "12/01/2024" could be M/D/Y or D/M/Y). Based on the prompt's explicit 
    # definition ("05/03/2024" -> day/month/year), we prioritize D/M/Y.

    formats_to_try = [
        # 1. ISO YYYY-MM-DD (Must be checked first)
        ("%Y-%m-%d", "ISO"),
        
        # 2. Day/Month/Year with slashes (D/M/Y). Handles flexible padding.
        # Example: "5/3/2024" or "05/03/2024"
        ("%d/%m/%Y", "Slashes D/M/Y"), 
        
        # 3. Full Month Name (Month Day, Year)
        # Example: "March 5, 2024"
        ("%B %d, %Y", "Full Month"),
        
        # 4. Abbreviated Month Name (Day Mon Year)
        # Example: "5 Mar 2024"
        ("%d %b %Y", "Abbreviated Month")
    ]

    for fmt_code, description in formats_to_try:
        try:
            # Attempt to parse the date using the current format code
            dt_object = datetime.datetime.strptime(text, fmt_code)
            
            # If successful, return it formatted as ISO YYYY-MM-DD
            return dt_object.strftime("%Y-%m-%d")

        except ValueError:
            # This specific format failed for the given text. Try the next one.
            continue
    
    # If all formats fail after trying them all, return None
    return None
