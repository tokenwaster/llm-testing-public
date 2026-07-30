import re
from datetime import date

FULL_MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}

ABBR_MONTHS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Format 1: ISO YYYY-MM-DD
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        try:
            date.fromisoformat(text)
            return text
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY or D/M/YYYY
    if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', text):
        day_str, month_str, year_str = text.split('/')
        try:
            day = int(day_str)
            month = int(month_str)
            year = int(year_str)
            date(year, month, day)  # validate
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return None

    # Format 3: MonthName Day, Year
    match = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text)
    if match:
        month_name = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))
        month = FULL_MONTHS.get(month_name)
        if month is not None:
            try:
                date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
        return None

    # Format 4: Day Mon Year (3-letter abbreviation)
    match = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if match:
        day = int(match.group(1))
        month_abbr = match.group(2).lower()
        year = int(match.group(3))
        month = ABBR_MONTHS.get(month_abbr)
        if month is not None:
            try:
                date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except ValueError:
                return None
        return None

    return None
