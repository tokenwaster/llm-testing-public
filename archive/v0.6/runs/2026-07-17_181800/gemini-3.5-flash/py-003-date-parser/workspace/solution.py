from datetime import datetime
import re

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Format 1: YYYY-MM-DD
    # We want to strictly match YYYY-MM-DD where YYYY is 4 digits, MM is 1-2 or 2 digits, DD is 1-2 or 2 digits.
    # Standard ISO is 4-2-2, but let's enforce exactly 4 digits for year, and 1-2 digits for month/day.
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', text):
        try:
            dt = datetime.strptime(text, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format 2: DD/MM/YYYY
    # Day/month/year with slashes, zero-padded or not.
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
        try:
            dt = datetime.strptime(text, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format 3: "March 5, 2024" (Full English month name, day, comma, 4-digit year)
    # Case-insensitive.
    if re.match(r'^[A-Za-z]+\s+\d{1,2},\s+\d{4}$', text):
        try:
            # Parse with %B %d, %Y
            dt = datetime.strptime(text, "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format 4: "5 Mar 2024" (day, 3-letter English month abbreviation, 4-digit year)
    # Case-insensitive.
    if re.match(r'^\d{1,2}\s+[A-Za-z]{3}\s+\d{4}$', text):
        try:
            dt = datetime.strptime(text, "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None
