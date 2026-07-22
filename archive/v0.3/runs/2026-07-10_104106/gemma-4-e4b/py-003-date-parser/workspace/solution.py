import datetime
from typing import Optional

def normalize_date(text: str) -> Optional[str]:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.

    Handles:
    1. "YYYY-MM-DD" (ISO)
    2. "D/M/Y" (Slashes, flexible padding)
    3. "Month D, YYYY" (Full English month name)
    4. "D Mon YYYY" (Abbreviated English month abbreviation)

    Returns None if the format is unrecognized or the date is invalid.
    """
    if not isinstance(text, str):
        return None

    cleaned_text = text.strip()

    # List of potential formats to try parsing in order of specificity/safety
    formats_to_try = [
        # 1. ISO format: YYYY-MM-DD
        ("%Y-%m-%d", "ISO"),

        # 2. Full Month Name: "March 5, 2024" (Month Day, Year)
        # Note: %B handles full month names and is case-insensitive.
        ("%B %d, %Y", "Full Month"),

        # 3. Abbreviated Month Name: "5 Mar 2024" (Day Mon Year)
        # Note: %b handles abbreviated month names and is case-insensitive.
        ("%d %b %Y", "Abbrev Month"),

        # 4. Day/Month/Year with slashes: "05/03/2024" or "5/3/2024"
        # We must try multiple slash variations to handle padding differences,
        # but since strptime is strict, we rely on the standard D/M/Y structure.
        # We will attempt a general pattern that handles slashes as separators.
        # Since Python's %d/%m/%Y often requires consistent padding, 
        # we must try parsing it directly and let ValueError catch failures.
        ("%d/%m/%Y", "D/M/Y (Padded)"),
    ]

    for fmt_str, name in formats_to_try:
        try:
            # Attempt to parse the date using the current format string
            dt_object = datetime.datetime.strptime(cleaned_text, fmt_str)
            
            # If successful, return the standardized ISO format
            return dt_object.strftime("%Y-%m-%d")

        except ValueError:
            # This specific format failed for this input string (or it's an invalid date like 31/02/2024)
            continue

    # Special handling for Format 2 flexibility (D/M/Y):
    # If the standard %d/%m/%Y fails, we try to handle cases where separators might be inconsistent
    # or padding is missing, although this pushes the limits of pure strptime usage.
    # We specifically check if the string looks like D/M/Y but failed above.
    if '/' in cleaned_text:
        try:
            # Attempting to parse it as a general date structure (D/M/Y) 
            # This is often necessary because strptime requires strict adherence to padding, 
            # and sometimes manual splitting/reformatting is needed for true flexibility.
            parts = cleaned_text.split('/')
            if len(parts) == 3:
                day, month, year = parts[0], parts[1], parts[2]
                # We use the standard format codes here, relying on strptime's internal logic
                # to handle single/double digits if possible, though it remains risky.
                dt_object = datetime.datetime.strptime(f"{day}/{month}/{year}", "%d/%m/%Y")
                return dt_object.strftime("%Y-%m-%d")

        except ValueError:
            pass # Failed even with manual attempt

    # If no format matched or all attempts failed (including invalid dates)
    return None
