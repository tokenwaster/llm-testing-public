from datetime import datetime
import re

def normalize_date(text: str) -> str | None:
    """
    Converts a date string from one of four specified formats to ISO YYYY-MM-DD.
    Returns None if parsing fails or the date is invalid.
    """
    if not isinstance(text, str):
        return None

    # Rule: Surrounding whitespace must be tolerated.
    cleaned_text = text.strip()

    # List of (format_string, description) tuples to attempt matching
    # Note on Format 2 (%d/%m/%Y): Python's standard library handles variations
    # in padding for day/month reasonably well when using explicit separators,
    # but complex flexible parsing might require preprocessing outside the scope
    # of simple strptime usage. We rely on standard behavior here.
    formats_to_try = [
        ("%Y-%m-%d", "ISO YYYY-MM-DD"), # Format 1: Already ISO
        (r"\b(\d{1,2})[/](\d{1,2})[/](\d{4})\b", "D/M/Y (flexible slashes)"), # Format 2: D/M/Y using regex capture groups for flexibility
        ("%B %d, %Y", "Full Month Name (e.g., March 5, 2024)"), # Format 3
        ("%d %b %Y", "Abbreviated Month Name (e.g., 5 Mar 2024)") # Format 4
    ]

    # --- Attempting parsing using structured formats first ---

    # 1. ISO YYYY-MM-DD (Must be exact match)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned_text):
        try:
            dt = datetime.strptime(cleaned_text, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass # Fall through if parsing fails (e.g., 2024-02-30)

    # --- Handling D/M/Y using flexible regex capture and manual datetime construction ---
    # This approach bypasses strict strptime padding rules for format 2, allowing 5/3/2024.
    if match := re.fullmatch(r"(\d{1,2})[/](\d{1,2})[/](\d{4})", cleaned_text):
        try:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            # Use combination to force validation (e.g., 31/02/2024 fails here)
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass # Invalid date like Feb 31st

    # --- Handling Format 3 (Full Month Name) and Format 4 (Abbreviated Month Name) using strptime ---
    
    # Note: %B and %b depend on the locale. We assume standard English locale.
    remaining_formats = [
        ("%B %d, %Y", "Format 3"), # March 5, 2024
        ("%d %b %Y", "Format 4")  # 5 Mar 2024
    ]

    for fmt, desc in remaining_formats:
        try:
            dt = datetime.strptime(cleaned_text, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue # Try the next format if this one fails

    # If no formats match or all attempts fail
    return None
