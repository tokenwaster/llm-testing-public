from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four supported formats to ISO YYYY-MM-DD.
    Returns None if the format is invalid or the date is not calendar valid.
    """
    cleaned_text = text.strip()

    # --- 1. Attempt Format: YYYY-MM-DD (ISO) ---
    try:
        dt = datetime.strptime(cleaned_text, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # --- 2. Attempt Format: D/M/Y (Slashes) ---
    # Handles flexible padding (e.g., '5/3/2024' or '05/03/2024')
    if all(c in '0123456789/' for c in cleaned_text):
        parts = [int(p) for p in cleaned_text.split('/')]
        if len(parts) == 3:
            try:
                day, month, year = parts[0], parts[1], parts[2]
                # datetime constructor handles validation (e.g., Feb 31st fails)
                dt = datetime(year, month, day)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass # Invalid calendar date

    # --- 3. Attempt Format: Full Month Name (Month Day, Year) ---
    # Example: "March 5, 2024"
    try:
        dt = datetime.strptime(cleaned_text, "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # --- 4. Attempt Format: Abbreviated Month Name (Day Mon Year) ---
    # Example: "5 Mar 2024"
    try:
        dt = datetime.strptime(cleaned_text, "%d %b %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # If none of the formats matched or resulted in a valid date
    return None
