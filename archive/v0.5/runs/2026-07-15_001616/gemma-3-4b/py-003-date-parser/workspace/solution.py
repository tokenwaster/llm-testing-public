import re

def normalize_date(text: str) -> str | None:
    """Converts a date string to ISO YYYY-MM-DD format."""

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

    # Format 3: Full English month name, day, comma, 4-digit year
    match = re.match(r"(\w+) (\d{1,2}), (\d{4})", text)
    if match:
        month_name, day, year = match.group(1), int(match.group(2)), int(match.group(3))
        months = ["january", "february", "march", "april", "may", "june",
                  "july", "august", "september", "october", "november", "december"]
        month_index = months.index(month_name.lower()) + 1
        if 1 <= day <= 31 and 1000 <= year <= 9999:
            return f"{year:04d}-{month_index:02d}-{day:02d}"

    # Format 4: Day, 3-letter English month abbreviation, 4-digit year
    match = re.match(r"(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})", text)
    if match:
        day, month_abbr, year = int(match.group(1)), match.group(2), int(match.group(3))
        months = ["jan", "feb", "mar", "apr", "may", "jun",
                  "jul", "aug", "sep", "oct", "nov", "dec"]
        month_index = months.index(month_abbr.lower()) + 1
        if 1 <= day <= 31 and 1000 <= year <= 9999:
            return f"{year:04d}-{month_index:02d}-{day:02d}"

    return None
