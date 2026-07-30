import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string from one of four specified formats to ISO YYYY-MM-DD.
    Returns None if the format is unrecognized or the date is invalid.
    """
    # Remove surrounding whitespace as required
    text = text.strip()
    if not text:
        return None

    # Define month mappings for validation and parsing
    full_months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    abbr_months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    # Format 1: "YYYY-MM-DD" (ISO)
    # We use \d{4}-\d{1,2}-\d{1,2} to allow for potential non-zero-padded inputs
    # while still validating the date.
    m1 = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', text)
    if m1:
        try:
            y, m, d = map(int, m1.groups())
            return datetime(y, m, d).strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 2: "DD/MM/YYYY" or "D/M/YYYY" (day/month/year with slashes)
    m2 = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', text)
    if m2:
        try:
            d, m, y = map(int, m2.groups())
            return datetime(y, m, d).strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Format 3: "Month Day, Year" (full English month name)
    m3 = re.match(r'^([a-zA-Z]+) (\d{1,2}), (\d{4})$', text)
    if m3:
        month_str, day_str, year_str = m3.groups()
        month_name = month_str.lower()
        # Ensure it is a full name as per the rule
        if month_name in full_months:
            try:
                day = int(day_str)
                year = int(year_str)
                return datetime(year, full_months[month_name], day).strftime('%Y-%m-%d')
            except ValueError:
                return None

    # Format 4: "D Mon YYYY" (day, 3-letter English month abbreviation, 4-digit year)
    m4 = re.match(r'^(\d{1,2}) ([a-zA-Z]{3}) (\d{4})$', text)
    if m4:
        day_str, month_abbr, year_str = m4.groups()
        month_key = month_abbr.lower()
        # Ensure it is a 3-letter abbreviation as per the rule
        if month_key in abbr_months:
            try:
                day = int(day_str)
                year = int(year_str)
                return datetime(year, abbr_months[month_key], day).strftime('%Y-%m-%d')
            except ValueError:
                return None

    # If no formats match or validation fails
    return None
