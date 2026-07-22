import datetime
from typing import Optional

def normalize_date(text: str) -> Optional[str]:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.

    Formats supported (case insensitive, whitespace tolerant):
    1. "YYYY-MM-DD" (ISO)
    2. "D/M/Y" (Day/Month/Year with slashes)
    3. "Month D, YYYY" (Full month name)
    4. "D Mon YYYY" (Abbreviated month name)

    Returns None if the format is invalid or the date is not a real calendar date.
    """
    text = text.strip()
    if not text:
        return None

    # List of potential formats and their corresponding strptime codes.
    # The order matters slightly, but since we use try/except, any order works.
    formats_to_try = [
        # 1. ISO format (YYYY-MM-DD) - Must check this first as it's the most rigid.
        ("%Y-%m-%d", "ISO"),

        # 2. Day/Month/Year (D/M/Y) - Handles both '5/3/2024' and '05/03/2024'
        (r"%d/%m/%Y", "DMY"),

        # 3. Full Month Name (Month D, YYYY)
        ("%B %d, %Y", "FullMonth"),

        # 4. Abbreviated Month Name (D Mon YYYY)
        ("%d %b %Y", "AbbrevMonth")
    ]

    for format_string, _ in formats_to_try:
        try:
            # Attempt to parse the date using the current format string
            dt_object = datetime.datetime.strptime(text, format_string)
            
            # If successful, return it formatted as ISO YYYY-MM-DD
            return dt_object.strftime("%Y-%m-%d")

        except ValueError:
            # This specific format failed for this input string. Try the next one.
            continue

    # If all formats fail to parse or validate (e.g., "31/02/2024"), return None.
    return None
