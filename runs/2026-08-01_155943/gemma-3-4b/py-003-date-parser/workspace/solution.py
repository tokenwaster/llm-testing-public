import re

def normalize_date(text: str) -> str | None:
    """Converts a date string in various formats to ISO YYYY-MM-DD."""

    text = text.strip()

    # Format 1: Already ISO
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text

    # Format 2: Day/Month/Year with slashes
    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= day <= 31 and 1 <= month <= 12 and 1000 <= year <= 9999:
            return f"{year:04d}-{month:02d}-{day:02d}"

    # Format 3: Full English Month Name, Day, Comma, Year
    match = re.match(r"([A-Za-z]+)\s+(\d+),\s+(\d{4})", text)
    if match:
        month_name = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))

        month_map = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }

        month = month_map.get(month_name)
        if month is None:
            return None
        if 1 <= day <= 31 and 1000 <= year <= 9999:
            return f"{year:04d}-{month:02d}-{day:02d}"

    # Format 4: Day, 3-letter English Month Abbreviation, Year
    match = re.match(r"(\d+)\s+(\w{3})\s+(\d{4})", text)
    if match:
        day = int(match.group(1))
        month_abbr = match.group(2).lower()
        year = int(match.group(3))

        month_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4,
            "may": 5, "jun": 6, "jul": 7, "aug": 8,
            "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }

        month = month_map.get(month_abbr)
        if month is None:
            return None
        if 1 <= day <= 31 and 1000 <= year <= 9999:
            return f"{year:04d}-{month:02d}-{day:02d}"

    return None
