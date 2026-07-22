import datetime
import re

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specific formats to ISO YYYY-MM-DD.
    Formats supported:
    1. "YYYY-MM-DD" (ISO)
    2. "D/M/YYYY" or "DD/MM/YYYY"
    3. "Month D, YYYY" (e.g., March 5, 2024)
    4. "D Mon YYYY" (e.g., 5 Mar 2024)

    Returns None if the format is invalid or the date is not a real calendar date.
    """
    # Remove surrounding whitespace
    text = text.strip()
    
    # Format 1: "YYYY-MM-DD" (ISO)
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
        try:
            dt = datetime.datetime.strptime(text, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format 2: "D/M/YYYY" or "DD/MM/YYYY" (e.g., 5/3/2024)
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
        try:
            dt = datetime.datetime.strptime(text, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format 3: "Month D, YYYY" (e.g., March 5, 2024)
    match3 = re.match(r'^([A-Za-z]+) (\d{1,2}), (\d{4})$', text)
    if match3:
        month_str, day_str, year_str = match3.groups()
        try:
            # Use title() to ensure case-insensitivity for month names (e.g., "march" -> "March")
            dt = datetime.datetime.strptime(f"{month_str.title()} {day_str}, {year_str}", "%B %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Format 4: "D Mon YYYY" (e.g., 5 Mar 2024)
    match4 = re.match(r'^(\d{1,2}) ([A-Za-z]{3}) (\d{4})$', text)
    if match4:
        day_str, month_abbr, year_str = match4.groups()
        try:
            # Use title() to ensure case-insensitivity for abbreviations (e.g., "mar" -> "Mar")
            dt = datetime.datetime.strptime(f"{day_str} {month_abbr.title()} {year_str}", "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None
