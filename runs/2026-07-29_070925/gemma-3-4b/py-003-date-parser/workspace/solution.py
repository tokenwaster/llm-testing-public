import re

def normalize_date(text: str) -> str | None:
    """Converts a date string in various formats to ISO YYYY-MM-DD."""

    text = text.strip()

    # Format 1: Already ISO
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        return text

    # Format 2: day/month/year with slashes
    if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", text):
        try:
            day, month, year = map(int, text.split("/"))
            if 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"
            else:
                return None
        except ValueError:
            return None

    # Format 3: full English month name, day, comma, 4-digit year
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    if re.match(r"^(\d{1,2})\s+(.+?),\s+(\d{4})$", text):
        day = int(re.search(r"(\d{1,2})", text).group(1))
        month_str = re.search(r"(.*?),", text).group(1).strip()
        year = int(re.search(r"(\d{4})$", text).group(1))

        try:
            month_index = month_names.index(month_str) + 1
            if 1 <= month_index <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month_index:02d}-{day:02d}"
            else:
                return None
        except ValueError:
            return None

    # Format 4: day, 3-letter English month abbreviation, 4-digit year
    month_abbreviations = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if re.match(r"^(\d{1,2})\s+(.+?),\s+(\d{4})$", text):
        day = int(re.search(r"(\d{1,2})", text).group(1))
        month_str = re.search(r"(.*?),", text).group(1).strip()
        year = int(re.search(r"(\d{4})$", text).group(1))

        try:
            month_index = month_abbreviations.index(month_str) + 1
            if 1 <= month_index <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month_index:02d}-{day:02d}"
            else:
                return None
        except ValueError:
            return None

    return None
