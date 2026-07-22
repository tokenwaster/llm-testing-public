import datetime
import re

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    Returns None if the format is invalid or the date does not exist on the calendar.
    """
    # Tolerate surrounding whitespace
    text = text.strip()
    if not text:
        return None

    # Format 1: "2024-03-05" — already ISO (validate it)
    # Strict check for YYYY-MM-DD format using regex to ensure zero-padding
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        try:
            dt = datetime.datetime.strptime(text, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Format 2: "05/03/2024" or "5/3/2024" — day/month/year with slashes
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
        try:
            dt = datetime.datetime.strptime(text, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Format 3: "March 5, 2024" — full English month name, day, comma, year
    if re.match(r'^[a-zA-Z]+ \d{1,2}, \d{4}$', text):
        try:
            # Month names are case-insensitive; normalize to Title Case for strptime
            parts = text.split(' ', 1)
            normalized = f"{parts[0].capitalize()} {parts[1]}"
            dt = datetime.datetime.strptime(normalized, "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Format 4: "5 Mar 2024" — day, 3-letter English month abbreviation, year
    if re.match(r'^\d{1,2} [a-zA-Z]{3} \d{4}$', text):
        try:
            # Month abbreviations are case-insensitive; normalize to Title Case for strptime
            parts = text.split(' ')
            normalized = f"{parts[0]} {parts[1].capitalize()} {parts[2]}"
            dt = datetime.datetime.strptime(normalized, "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Return None if the text does not match any of the four supported formats
    return None
