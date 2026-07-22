import datetime
from typing import Optional

def normalize_date(text: str) -> Optional[str]:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.

    Handles:
    1. YYYY-MM-DD (ISO)
    2. D/M/Y (e.g., 5/3/2024)
    3. Full Month Name (e.g., March 5, 2024)
    4. Abbreviated Month Name (e.g., 5 Mar 2024)

    Returns None if the format is invalid or the date is not a real calendar date.
    """
    if not isinstance(text, str):
        return None

    # Rule: Surrounding whitespace must be tolerated.
    cleaned_text = text.strip()

    # List of potential formats to try, ordered by specificity/likelihood
    formats_to_try = [
        ("%Y-%m-%d", "ISO"),  # 1. YYYY-MM-DD (Already ISO)
        (r"\d{1,2}/\d{1,2}/\d{4}", "D/M/Y"), # 2. D/M/Y (Using regex check first for structure)
        ("%B %d, %Y", "Full Month Name"),  # 3. Full English month name
        ("%d %b %Y", "Abbreviated Month Name") # 4. Day, 3-letter abbreviation
    ]

    # --- Attempt Parsing ---

    # 1. ISO Format (YYYY-MM-DD)
    try:
        dt_obj = datetime.datetime.strptime(cleaned_text, "%Y-%m-%d")
        return dt_obj.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # 2. D/M/Y Format (e.g., 5/3/2024)
    # We rely on strptime's ability to handle single digits and the specified order (D/M/Y).
    try:
        dt_obj = datetime.datetime.strptime(cleaned_text, "%d/%m/%Y")
        return dt_obj.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # 3. Full Month Name (e.g., March 5, 2024)
    try:
        dt_obj = datetime.datetime.strptime(cleaned_text, "%B %d, %Y")
        return dt_obj.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # 4. Abbreviated Month Name (e.g., 5 Mar 2024)
    try:
        dt_obj = datetime.datetime.strptime(cleaned_text, "%d %b %Y")
        return dt_obj.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # If none of the formats matched or if strptime failed due to invalid date/format
    return None
