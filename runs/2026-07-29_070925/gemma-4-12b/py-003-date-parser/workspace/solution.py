from datetime import datetime

def normalize_date(text: str) -> str | None:
    """
    Converts a date string in one of four specified formats to ISO YYYY-MM-DD.
    Supported formats:
    1. "YYYY-MM-DD" (ISO)
    2. "D/M/YYYY" or "DD/MM/YYYY" (Day/Month/Year with slashes)
    3. "Month D, YYYY" (Full English month name, day, comma, 4-digit year)
    4. "D Mon YYYY" (Day, 3-letter abbreviation, 4-digit year)

    Returns None for invalid dates or formats that do not match the requirements.
    """
    # Remove surrounding whitespace
    text = text.strip()
    
    if not text:
        return None

    # The four target formats provided in the prompt:
    # %Y-%m-%d handles "2024-03-05"
    # %d/%m/%Y handles "05/03/2024" and "5/3/2024"
    # %B %d, %Y handles "March 5, 2024" (with comma)
    # %d %b %Y handles "5 Mar 2024"
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y", "%d %b %Y"]

    # To handle case-insensitivity for month names/abbreviations while 
    # keeping the logic simple, we try parsing the original text first, 
    # then a title-cased version. .title() correctly handles "march" -> "March"
    # and "MAR" -> "Mar", without affecting digits or slashes.
    candidates = [text, text.title()]

    for candidate in candidates:
        for fmt in formats:
            try:
                # strptime validates calendar dates (e.g., rejects 31/02/2024)
                dt = datetime.strptime(candidate, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

    return None
