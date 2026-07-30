import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in specific formats to ISO YYYY-MM-DD.
    
    Supported formats (whitespace stripped, case-insensitive month names):
    1. "YYYY-MM-DD" (ISO) - strict validation required.
    2. "DD/MM/YYYY" or "D/M/YYYY" (Day/Week? No, Day/Month).
    3. "Month D, YYYY" (Full name with comma).
    4. "D Mon YYYY" (Abbreviation).
    
    Returns None for invalid format or non-existent date.
    """
    text = text.strip()

    # Format 1: ISO YYYY-MM-DD (Strictly formatted)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        try:
            dt = datetime.strptime(text, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Format 2: DD/MM/YYYY or D/M/YYYY (Slashes) - Day/Week? No, Day/Month.
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
        try:
            dt = datetime.strptime(text, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Format 3: Full Month Name Day, Year (e.g. "March 5, 2024")
    if re.match(r'^[A-Za-z]+ \d{1,2}, \d{4}$', text):
        try:
            dt = datetime.strptime(text, '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Format 4: Day Abbreviation Year (e.g. "5 Mar 2024") - Month abbreviation is typically 3 letters
    if re.match(r'^\d{1,2} [A-Za-z]{3} \d{4}$', text):
        try:
            dt = datetime.strptime(text, '%d %b %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    return None
