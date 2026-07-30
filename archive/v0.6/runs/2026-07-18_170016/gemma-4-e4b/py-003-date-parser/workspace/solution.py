import datetime
from typing import Optional

def normalize_date(text: str) -> Optional[str]:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.

    Formats supported (case-insensitive month names/abbreviations):
    1. YYYY-MM-DD (ISO standard)
    2. D/M/Y (e.g., 5/3/2024)
    3. Full Month Name (e.g., March 5, 2024)
    4. Abbreviated Month Name (e.g., 5 Mar 2024)

    Returns None if the format is invalid or the date is not a real calendar date.
    """
    text = text.strip()
    if not text:
        return None

    # List of potential formats to try, ordered by specificity/likelihood
    formats_to_try = [
        ("%Y-%m-%d", "ISO"),  # 1. YYYY-MM-DD
        ("%d/%m/%Y", "D/M/Y"), # 2. D/M/Y (Handles optional padding due to strptime flexibility)
        ("%B %d, %Y", "Full Month"), # 3. Full English month name
        ("%d %b %Y", "Abbreviated Month") # 4. Day, 3-letter abbreviation
    ]

    for format_string, _ in formats_to_try:
        try:
            # Attempt to parse the date using the current format string
            dt_obj = datetime.datetime.strptime(text, format_string)
            
            # If successful, convert to date object and return ISO format
            return dt_obj.date().isoformat()

        except ValueError:
            # This handles cases where the input doesn't match the format 
            # OR if it matches the format but represents an impossible date (e.g., Feb 30th).
            continue

    # If no formats matched or all attempts failed validation
    return None
